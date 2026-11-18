#include <arpa/inet.h>
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <atomic>
#include <cstdint>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

#include "exceptionsbase.h"
#include "snmpstatus.h"

namespace {

// Minimal ASN.1 BER helpers for an in-process loopback SNMPv2c responder.
void append_length(std::vector<uint8_t> &out, size_t len) {
   if (len < 0x80) {
      out.push_back(static_cast<uint8_t>(len));
   } else if (len <= 0xFF) {
      out.push_back(0x81);
      out.push_back(static_cast<uint8_t>(len));
   } else {
      out.push_back(0x82);
      out.push_back(static_cast<uint8_t>((len >> 8) & 0xFF));
      out.push_back(static_cast<uint8_t>(len & 0xFF));
   }
}

void append_tlv(std::vector<uint8_t> &out, uint8_t tag, std::vector<uint8_t> const &val) {
   out.push_back(tag);
   append_length(out, val.size());
   out.insert(out.end(), val.begin(), val.end());
}

void append_int_tag(std::vector<uint8_t> &out, uint8_t tag, int64_t value) {
   std::vector<uint8_t> bytes;
   if (value == 0) {
      bytes.push_back(0);
   } else {
      uint64_t uval = static_cast<uint64_t>(value);
      std::vector<uint8_t> tmp;
      while (uval > 0) {
         tmp.push_back(static_cast<uint8_t>(uval & 0xFF));
         uval >>= 8;
      }
      if (tmp.back() & 0x80) {
         tmp.push_back(0x00);
      }
      bytes.assign(tmp.rbegin(), tmp.rend());
   }
   append_tlv(out, tag, bytes);
}

std::vector<uint8_t> encode_oid_body(std::vector<uint32_t> const &oid_vec) {
   std::vector<uint8_t> body;
   if (oid_vec.size() >= 2) {
      body.push_back(static_cast<uint8_t>(oid_vec[0] * 40 + oid_vec[1]));
      for (size_t i = 2; i < oid_vec.size(); ++i) {
         uint32_t v = oid_vec[i];
         uint8_t buf[5];
         int n = 0;
         buf[n++] = static_cast<uint8_t>(v & 0x7F);
         v >>= 7;
         while (v > 0) {
            buf[n++] = static_cast<uint8_t>((v & 0x7F) | 0x80);
            v >>= 7;
         }
         for (int j = n - 1; j >= 0; --j) {
            body.push_back(buf[j]);
         }
      }
   }
   return body;
}

bool read_len(uint8_t const *data, size_t total, size_t &pos, size_t &len_out) {
   if (pos >= total) {
      return false;
   }
   uint8_t b = data[pos++];
   if ((b & 0x80) == 0) {
      len_out = b;
      return pos + len_out <= total;
   }
   size_t num_bytes = b & 0x7F;
   if (num_bytes == 0 || num_bytes > 4 || pos + num_bytes > total) {
      return false;
   }
   len_out = 0;
   for (size_t i = 0; i < num_bytes; ++i) {
      len_out = (len_out << 8) | data[pos++];
   }
   return pos + len_out <= total;
}

bool decode_oid(uint8_t const *data, size_t len, std::vector<uint32_t> &oid_out) {
   oid_out.clear();
   if (len == 0) {
      return false;
   }
   uint8_t first = data[0];
   oid_out.push_back(first / 40);
   oid_out.push_back(first % 40);
   size_t i = 1;
   while (i < len) {
      uint32_t sub = 0;
      while (i < len) {
         uint8_t b = data[i++];
         sub = (sub << 7) | (b & 0x7F);
         if ((b & 0x80) == 0) {
            break;
         }
      }
      oid_out.push_back(sub);
   }
   return true;
}

struct ParsedRequest {
   std::vector<uint8_t> version_bytes;
   std::vector<uint8_t> community_bytes;
   uint8_t pdu_tag = 0;
   std::vector<uint8_t> req_id_bytes;
   std::vector<std::vector<uint32_t>> oids;
};

bool parse_snmp_request(uint8_t const *buf, size_t len, ParsedRequest &req) {
   size_t pos = 0;
   if (pos >= len || buf[pos++] != 0x30) {
      return false;
   }
   size_t seq_len = 0;
   if (!read_len(buf, len, pos, seq_len)) {
      return false;
   }
   // version
   if (pos >= len || buf[pos++] != 0x02) {
      return false;
   }
   size_t vlen = 0;
   if (!read_len(buf, len, pos, vlen)) {
      return false;
   }
   req.version_bytes.assign(buf + pos, buf + pos + vlen);
   pos += vlen;
   // community
   if (pos >= len || buf[pos++] != 0x04) {
      return false;
   }
   size_t clen = 0;
   if (!read_len(buf, len, pos, clen)) {
      return false;
   }
   req.community_bytes.assign(buf + pos, buf + pos + clen);
   pos += clen;
   // PDU
   if (pos >= len) {
      return false;
   }
   req.pdu_tag = buf[pos++];
   size_t pdu_len = 0;
   if (!read_len(buf, len, pos, pdu_len)) {
      return false;
   }
   // request-id
   if (pos >= len || buf[pos++] != 0x02) {
      return false;
   }
   size_t rid_len = 0;
   if (!read_len(buf, len, pos, rid_len)) {
      return false;
   }
   req.req_id_bytes.assign(buf + pos, buf + pos + rid_len);
   pos += rid_len;
   // error-status & error-index
   for (int i = 0; i < 2; ++i) {
      if (pos >= len || buf[pos++] != 0x02) {
         return false;
      }
      size_t elen = 0;
      if (!read_len(buf, len, pos, elen)) {
         return false;
      }
      pos += elen;
   }
   // varbind list
   if (pos >= len || buf[pos++] != 0x30) {
      return false;
   }
   size_t vbl_len = 0;
   if (!read_len(buf, len, pos, vbl_len)) {
      return false;
   }
   size_t vbl_end = pos + vbl_len;
   while (pos < vbl_end) {
      if (buf[pos++] != 0x30) {
         return false;
      }
      size_t vb_len = 0;
      if (!read_len(buf, len, pos, vb_len)) {
         return false;
      }
      size_t vb_end = pos + vb_len;
      if (pos >= vb_end || buf[pos++] != 0x06) {
         return false;
      }
      size_t oid_len = 0;
      if (!read_len(buf, len, pos, oid_len)) {
         return false;
      }
      std::vector<uint32_t> oid_vec;
      if (!decode_oid(buf + pos, oid_len, oid_vec)) {
         return false;
      }
      req.oids.push_back(std::move(oid_vec));
      pos = vb_end;
   }
   return true;
}

struct VarBindResp {
   std::vector<uint32_t> oid;
   uint8_t tag;
   std::vector<uint8_t> raw_val;
   int64_t int_val = 0;
   bool is_int_type = false;
};

std::vector<uint8_t> build_snmp_response(ParsedRequest const &req,
                                         int errstat,
                                         int errindex,
                                         std::vector<VarBindResp> const &vbs) {
   std::vector<uint8_t> vbl_body;
   for (auto const &vb : vbs) {
      std::vector<uint8_t> vb_body;
      append_tlv(vb_body, 0x06, encode_oid_body(vb.oid));
      if (vb.is_int_type) {
         append_int_tag(vb_body, vb.tag, vb.int_val);
      } else {
         append_tlv(vb_body, vb.tag, vb.raw_val);
      }
      append_tlv(vbl_body, 0x30, vb_body);
   }

   std::vector<uint8_t> pdu_body;
   append_tlv(pdu_body, 0x02, req.req_id_bytes);
   append_int_tag(pdu_body, 0x02, errstat);
   append_int_tag(pdu_body, 0x02, errindex);
   append_tlv(pdu_body, 0x30, vbl_body);

   std::vector<uint8_t> msg_body;
   append_tlv(msg_body, 0x02, req.version_bytes);
   append_tlv(msg_body, 0x04, req.community_bytes);
   append_tlv(msg_body, 0xA2, pdu_body);

   std::vector<uint8_t> out;
   append_tlv(out, 0x30, msg_body);
   return out;
}

class MockSnmpStatusServer {
  public:
   struct Config {
      std::string sys_descr = "MockLinux 6.1";
      int64_t sys_uptime = 123456;
      int64_t ip_in_receives = 42;
      int64_t ip_out_requests = 84;
      std::vector<int> if_oper_statuses = {1, 2, 2};
      int get_errstat = 0;
      int get_errindex = 0;
      bool fail_first_get_only = false;
      int getnext_errstat = 0;
      int getnext_errindex = 0;
      bool drop_getnext = false;
   };

   explicit MockSnmpStatusServer(Config cfg) : cfg_(std::move(cfg)) {
      sock_ = ::socket(AF_INET, SOCK_DGRAM, 0);
      if (sock_ < 0) {
         return;
      }
      sockaddr_in addr{};
      addr.sin_family = AF_INET;
      addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
      addr.sin_port = 0;
      if (::bind(sock_, reinterpret_cast<sockaddr *>(&addr), sizeof(addr)) < 0) {
         ::close(sock_);
         sock_ = -1;
         return;
      }
      socklen_t alen = sizeof(addr);
      if (::getsockname(sock_, reinterpret_cast<sockaddr *>(&addr), &alen) == 0) {
         port_ = ntohs(addr.sin_port);
      }
      timeval tv{};
      tv.tv_sec = 0;
      tv.tv_usec = 50000;
      ::setsockopt(sock_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

      running_ = true;
      thread_ = std::thread([this]() { serve(); });
   }

   ~MockSnmpStatusServer() {
      running_ = false;
      if (thread_.joinable()) {
         thread_.join();
      }
      if (sock_ >= 0) {
         ::close(sock_);
      }
   }

   std::string target() const { return "127.0.0.1:" + std::to_string(port_); }

  private:
   void serve() {
      uint8_t buf[4096];
      int get_count = 0;
      while (running_) {
         sockaddr_in client{};
         socklen_t clen = sizeof(client);
         ssize_t n =
             ::recvfrom(sock_, buf, sizeof(buf), 0, reinterpret_cast<sockaddr *>(&client), &clen);
         if (n <= 0) {
            continue;
         }
         ParsedRequest req;
         if (!parse_snmp_request(buf, static_cast<size_t>(n), req)) {
            continue;
         }
         if (req.pdu_tag == 0xA0) { // GetRequest
            get_count++;
            int errstat = cfg_.get_errstat;
            int errindex = cfg_.get_errindex;
            if (cfg_.fail_first_get_only && get_count > 1) {
               errstat = 0;
               errindex = 0;
            }
            std::vector<VarBindResp> vbs;
            for (auto const &oid_vec : req.oids) {
               VarBindResp vb;
               vb.oid = oid_vec;
               if (oid_vec == std::vector<uint32_t>{1, 3, 6, 1, 2, 1, 1, 1, 0}) {
                  vb.tag = 0x04;
                  vb.raw_val.assign(cfg_.sys_descr.begin(), cfg_.sys_descr.end());
               } else if (oid_vec == std::vector<uint32_t>{1, 3, 6, 1, 2, 1, 1, 3, 0}) {
                  vb.tag = 0x43;
                  vb.int_val = cfg_.sys_uptime;
                  vb.is_int_type = true;
               } else if (oid_vec == std::vector<uint32_t>{1, 3, 6, 1, 2, 1, 4, 3, 0}) {
                  vb.tag = 0x41;
                  vb.int_val = cfg_.ip_in_receives;
                  vb.is_int_type = true;
               } else if (oid_vec == std::vector<uint32_t>{1, 3, 6, 1, 2, 1, 4, 10, 0}) {
                  vb.tag = 0x41;
                  vb.int_val = cfg_.ip_out_requests;
                  vb.is_int_type = true;
               } else {
                  vb.tag = 0x05;
               }
               vbs.push_back(std::move(vb));
            }
            auto resp = build_snmp_response(req, errstat, errindex, vbs);
            ::sendto(sock_, resp.data(), resp.size(), 0, reinterpret_cast<sockaddr *>(&client),
                     clen);
         } else if (req.pdu_tag == 0xA1) { // GetNextRequest
            if (cfg_.drop_getnext) {
               continue;
            }
            if (cfg_.getnext_errstat != 0) {
               std::vector<VarBindResp> vbs;
               for (auto const &oid_vec : req.oids) {
                  VarBindResp vb;
                  vb.oid = oid_vec;
                  vb.tag = 0x05;
                  vbs.push_back(std::move(vb));
               }
               auto resp =
                   build_snmp_response(req, cfg_.getnext_errstat, cfg_.getnext_errindex, vbs);
               ::sendto(sock_, resp.data(), resp.size(), 0, reinterpret_cast<sockaddr *>(&client),
                        clen);
               continue;
            }

            std::vector<VarBindResp> vbs;
            for (auto const &oid_vec : req.oids) {
               // Base OIDs have length 10: 1.3.6.1.2.1.2.2.1.<col>
               // Instance OIDs have length 11: 1.3.6.1.2.1.2.2.1.<col>.<idx>
               size_t next_idx = 1;
               if (oid_vec.size() >= 11) {
                  next_idx = oid_vec[10] + 1;
               }
               VarBindResp vb;
               if (next_idx <= cfg_.if_oper_statuses.size() && oid_vec.size() >= 10) {
                  vb.oid.assign(oid_vec.begin(), oid_vec.begin() + 10);
                  vb.oid.push_back(static_cast<uint32_t>(next_idx));
                  uint32_t col = oid_vec[9];
                  if (col == 8) {
                     vb.tag = 0x02; // ASN_INTEGER
                     vb.int_val = cfg_.if_oper_statuses[next_idx - 1];
                  } else if (col == 11) {
                     vb.tag = 0x41; // ASN_COUNTER
                     vb.int_val = 10;
                  } else if (col == 12) {
                     vb.tag = 0x41;
                     vb.int_val = 2;
                  } else if (col == 17) {
                     vb.tag = 0x41;
                     vb.int_val = 20;
                  } else { // col == 18
                     vb.tag = 0x41;
                     vb.int_val = 3;
                  }
                  vb.is_int_type = true;
               } else {
                  vb.oid = oid_vec;
                  vb.tag = 0x82; // endOfMibView
               }
               vbs.push_back(std::move(vb));
            }
            auto resp = build_snmp_response(req, 0, 0, vbs);
            ::sendto(sock_, resp.data(), resp.size(), 0, reinterpret_cast<sockaddr *>(&client),
                     clen);
         }
      }
   }

   Config cfg_;
   int sock_ = -1;
   uint16_t port_ = 0;
   std::atomic<bool> running_{false};
   std::thread thread_;
};

} // namespace

class SnmpStatusTest : public ::testing::Test {
  protected:
   void SetUp() override { netsnmp_ds_set_boolean(NETSNMP_DS_APPLICATION_ID, 0, 0); }
   void TearDown() override { netsnmp_ds_set_boolean(NETSNMP_DS_APPLICATION_ID, 0, 0); }
};

TEST_F(SnmpStatusTest, TestHelpThrowsParseError) {
   std::vector<std::string> args = {"-h"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_help"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestVersionThrowsParseError) {
   std::vector<std::string> args = {"-V"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_version"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestEmptyArgsThrowsParseError) {
   std::vector<std::string> args = {};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_empty"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestInvalidOptionThrowsParseError) {
   std::vector<std::string> args = {"-Z", "localhost:11161"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_invalid_opt"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestInvalidCOptionThrowsParseError) {
   std::vector<std::string> args = {"-CX", "-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_invalid_c"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestTimeoutOnUnreachableHost) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public",         "-t",
                                    "1",  "-r", "0",  "127.0.0.1:19999"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_timeout"), TimeoutErrorBase);
}

TEST_F(SnmpStatusTest, TestDontFixPdusOptionAcceptedBeforeTimeout) {
   std::vector<std::string> args = {"-Cf", "-v", "2c", "-c", "public",
                                    "-t",  "1",  "-r", "0",  "127.0.0.1:19999"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_cf_timeout"), TimeoutErrorBase);
}

TEST_F(SnmpStatusTest, TestInvalidTransportThrowsConnectionError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "unix:/nonexistent_ezsnmp_sock"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_conn_err"), ConnectionErrorBase);
}

TEST_F(SnmpStatusTest, TestSuccessMultipleInterfacesAndDownCount) {
   MockSnmpStatusServer::Config cfg;
   cfg.if_oper_statuses = {1, 2, 2};
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-v", "2c", "-c", "public", server.target()};
   auto res = snmpstatus(args, "testing_snmpstatus_ok_multi");
   ASSERT_EQ(res.size(), 3u);
   EXPECT_NE(res[0].find("MockLinux 6.1"), std::string::npos);
   EXPECT_NE(res[0].find("Up:"), std::string::npos);
   EXPECT_EQ(res[1], "Interfaces: 3, Recv/Trans packets: 36/69 | IP: 42/84");
   EXPECT_EQ(res[2], "2 interfaces are down!");
}

TEST_F(SnmpStatusTest, TestSuccessOneDownInterface) {
   MockSnmpStatusServer::Config cfg;
   cfg.if_oper_statuses = {1, 2};
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-v", "2c", "-c", "public", server.target()};
   auto res = snmpstatus(args, "testing_snmpstatus_ok_one_down");
   ASSERT_EQ(res.size(), 3u);
   EXPECT_EQ(res[1], "Interfaces: 2, Recv/Trans packets: 24/46 | IP: 42/84");
   EXPECT_EQ(res[2], "1 interface is down!");
}

TEST_F(SnmpStatusTest, TestSuccessNoDownInterfaces) {
   MockSnmpStatusServer::Config cfg;
   cfg.if_oper_statuses = {1};
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-v", "2c", "-c", "public", server.target()};
   auto res = snmpstatus(args, "testing_snmpstatus_ok_no_down");
   ASSERT_EQ(res.size(), 2u);
   EXPECT_EQ(res[1], "Interfaces: 1, Recv/Trans packets: 12/23 | IP: 42/84");
}

TEST_F(SnmpStatusTest, TestGetRetryWithFixPdu) {
   MockSnmpStatusServer::Config cfg;
   cfg.if_oper_statuses = {1};
   cfg.get_errstat = SNMP_ERR_NOSUCHNAME;
   cfg.get_errindex = 3;
   cfg.fail_first_get_only = true;
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-v", "2c", "-c", "public", server.target()};
   auto res = snmpstatus(args, "testing_snmpstatus_fix_pdu");
   ASSERT_EQ(res.size(), 2u);
   EXPECT_EQ(res[1], "Interfaces: 1, Recv/Trans packets: 12/23 | IP: 0/84");
}

TEST_F(SnmpStatusTest, TestGetErrorWithDontFixPdusThrowsPacketError) {
   MockSnmpStatusServer::Config cfg;
   cfg.get_errstat = SNMP_ERR_NOSUCHNAME;
   cfg.get_errindex = 3;
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-Cf", "-v", "2c", "-c", "public", server.target()};
   EXPECT_THROW(
       {
          try {
             snmpstatus(args, "testing_snmpstatus_cf_err");
          } catch (PacketErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_NE(msg.find("Error in packet."), std::string::npos);
             EXPECT_NE(msg.find("Failed object:"), std::string::npos);
             throw;
          }
       },
       PacketErrorBase);
}

TEST_F(SnmpStatusTest, TestGetUnfixableErrorThrowsPacketError) {
   MockSnmpStatusServer::Config cfg;
   cfg.get_errstat = SNMP_ERR_GENERR;
   cfg.get_errindex = 0;
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-v", "2c", "-c", "public", server.target()};
   EXPECT_THROW(
       {
          try {
             snmpstatus(args, "testing_snmpstatus_generr");
          } catch (PacketErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_NE(msg.find("Error in packet."), std::string::npos);
             EXPECT_EQ(msg.find("Failed object:"), std::string::npos);
             throw;
          }
       },
       PacketErrorBase);
}

TEST_F(SnmpStatusTest, TestGetNextErrorThrowsPacketError) {
   MockSnmpStatusServer::Config cfg;
   cfg.getnext_errstat = SNMP_ERR_GENERR;
   cfg.getnext_errindex = 1;
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-v", "2c", "-c", "public", server.target()};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_getnext_err"), PacketErrorBase);
}

TEST_F(SnmpStatusTest, TestGetNextTimeoutThrowsTimeoutError) {
   MockSnmpStatusServer::Config cfg;
   cfg.drop_getnext = true;
   MockSnmpStatusServer server(cfg);

   std::vector<std::string> args = {"-v", "2c", "-c", "public",       "-t",
                                    "1",  "-r", "0",  server.target()};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_getnext_timeout"), TimeoutErrorBase);
}
