#include <arpa/inet.h>
#include <gtest/gtest.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <string>
#include <thread>
#include <vector>

#include "exceptionsbase.h"
#include "snmpdf.h"

namespace {

bool is_test_snmpd_available() {
   return std::system(
              "snmpget -v2c -c public -t 1 -r 0 udp:127.0.0.1:11161 "
              ".1.3.6.1.2.1.1.1.0 >/dev/null 2>&1") == 0;
}

// Minimal BER / SNMPv2c loopback UDP responder for deterministic unit tests.
struct MockVarbind {
   enum class Type : uint8_t {
      Integer = 0x02,
      OctetString = 0x04,
      Null = 0x05,
      Oid = 0x06,
      NoSuchObject = 0x80,
      NoSuchInstance = 0x81,
      EndOfMibView = 0x82,
   };

   std::vector<uint32_t> oid;
   Type type = Type::Null;
   int64_t int_val = 0;
   std::string str_val;
   std::vector<uint32_t> oid_val;
};

struct MockRequest {
   int64_t version = 1;
   std::string community;
   uint8_t pdu_type = 0; // 0xA0 = GetRequest, 0xA1 = GetNextRequest
   int64_t request_id = 0;
   std::vector<std::vector<uint32_t>> oids;
};

struct MockResponse {
   bool drop = false;
   int64_t error_status = 0;
   int64_t error_index = 0;
   std::vector<MockVarbind> varbinds;
};

bool read_length(uint8_t const *buf, size_t len, size_t &pos, size_t &out_len) {
   if (pos >= len) {
      return false;
   }
   uint8_t first = buf[pos++];
   if ((first & 0x80) == 0) {
      out_len = first;
      return pos + out_len <= len;
   }
   size_t num_bytes = first & 0x7F;
   if (num_bytes == 0 || num_bytes > sizeof(size_t) || pos + num_bytes > len) {
      return false;
   }
   out_len = 0;
   for (size_t i = 0; i < num_bytes; ++i) {
      out_len = (out_len << 8) | buf[pos++];
   }
   return pos + out_len <= len;
}

bool read_integer(uint8_t const *buf, size_t len, size_t &pos, int64_t &out_val) {
   if (pos >= len || buf[pos] != 0x02) {
      return false;
   }
   ++pos;
   size_t val_len = 0;
   if (!read_length(buf, len, pos, val_len) || val_len == 0 || val_len > 8) {
      return false;
   }
   int64_t v = (buf[pos] & 0x80) ? -1 : 0;
   for (size_t i = 0; i < val_len; ++i) {
      v = (v << 8) | buf[pos++];
   }
   out_val = v;
   return true;
}

bool read_oid(uint8_t const *buf, size_t len, size_t &pos, std::vector<uint32_t> &out_oid) {
   if (pos >= len || buf[pos] != 0x06) {
      return false;
   }
   ++pos;
   size_t oid_len = 0;
   if (!read_length(buf, len, pos, oid_len) || oid_len == 0) {
      return false;
   }
   size_t end = pos + oid_len;
   uint8_t first = buf[pos++];
   out_oid.clear();
   out_oid.push_back(first / 40);
   out_oid.push_back(first % 40);
   while (pos < end) {
      uint32_t subid = 0;
      uint8_t b = 0;
      do {
         if (pos >= end) {
            return false;
         }
         b = buf[pos++];
         subid = (subid << 7) | (b & 0x7F);
      } while (b & 0x80);
      out_oid.push_back(subid);
   }
   return true;
}

bool decode_snmp_request(uint8_t const *buf, size_t len, MockRequest &req) {
   size_t pos = 0;
   if (pos >= len || buf[pos++] != 0x30) {
      return false;
   }
   size_t msg_len = 0;
   if (!read_length(buf, len, pos, msg_len)) {
      return false;
   }
   if (!read_integer(buf, len, pos, req.version)) {
      return false;
   }
   if (pos >= len || buf[pos++] != 0x04) {
      return false;
   }
   size_t comm_len = 0;
   if (!read_length(buf, len, pos, comm_len)) {
      return false;
   }
   req.community.assign(reinterpret_cast<char const *>(buf + pos), comm_len);
   pos += comm_len;
   if (pos >= len) {
      return false;
   }
   req.pdu_type = buf[pos++];
   size_t pdu_len = 0;
   if (!read_length(buf, len, pos, pdu_len)) {
      return false;
   }
   if (!read_integer(buf, len, pos, req.request_id)) {
      return false;
   }
   int64_t err_stat = 0;
   int64_t err_idx = 0;
   if (!read_integer(buf, len, pos, err_stat) || !read_integer(buf, len, pos, err_idx)) {
      return false;
   }
   if (pos >= len || buf[pos++] != 0x30) {
      return false;
   }
   size_t vbl_len = 0;
   if (!read_length(buf, len, pos, vbl_len)) {
      return false;
   }
   size_t vbl_end = pos + vbl_len;
   while (pos < vbl_end) {
      if (buf[pos++] != 0x30) {
         return false;
      }
      size_t vb_len = 0;
      if (!read_length(buf, len, pos, vb_len)) {
         return false;
      }
      size_t vb_end = pos + vb_len;
      std::vector<uint32_t> oid;
      if (!read_oid(buf, len, pos, oid)) {
         return false;
      }
      req.oids.push_back(std::move(oid));
      pos = vb_end;
   }
   return true;
}

void write_length(std::vector<uint8_t> &out, size_t len) {
   if (len < 0x80) {
      out.push_back(static_cast<uint8_t>(len));
   } else {
      std::vector<uint8_t> bytes;
      while (len > 0) {
         bytes.push_back(static_cast<uint8_t>(len & 0xFF));
         len >>= 8;
      }
      out.push_back(static_cast<uint8_t>(0x80 | bytes.size()));
      for (auto it = bytes.rbegin(); it != bytes.rend(); ++it) {
         out.push_back(*it);
      }
   }
}

void wrap_tlv(uint8_t tag, std::vector<uint8_t> const &payload, std::vector<uint8_t> &out) {
   out.push_back(tag);
   write_length(out, payload.size());
   out.insert(out.end(), payload.begin(), payload.end());
}

void encode_integer(int64_t val, std::vector<uint8_t> &out) {
   std::vector<uint8_t> bytes;
   uint64_t uval = static_cast<uint64_t>(val);
   do {
      bytes.push_back(static_cast<uint8_t>(uval & 0xFF));
      uval >>= 8;
   } while (uval > 0 && !(val < 0 && uval == static_cast<uint64_t>(-1) >> 8));
   if (val >= 0 && (bytes.back() & 0x80)) {
      bytes.push_back(0x00);
   } else if (val < 0 && !(bytes.back() & 0x80)) {
      bytes.push_back(0xFF);
   }
   std::vector<uint8_t> payload(bytes.rbegin(), bytes.rend());
   wrap_tlv(0x02, payload, out);
}

void encode_oid(std::vector<uint32_t> const &oid, std::vector<uint8_t> &out) {
   std::vector<uint8_t> payload;
   if (oid.size() >= 2) {
      payload.push_back(static_cast<uint8_t>(oid[0] * 40 + oid[1]));
      for (size_t i = 2; i < oid.size(); ++i) {
         uint32_t v = oid[i];
         std::vector<uint8_t> sub;
         sub.push_back(static_cast<uint8_t>(v & 0x7F));
         v >>= 7;
         while (v > 0) {
            sub.push_back(static_cast<uint8_t>((v & 0x7F) | 0x80));
            v >>= 7;
         }
         for (auto it = sub.rbegin(); it != sub.rend(); ++it) {
            payload.push_back(*it);
         }
      }
   }
   wrap_tlv(0x06, payload, out);
}

std::vector<uint8_t> encode_snmp_response(MockRequest const &req, MockResponse const &resp) {
   std::vector<uint8_t> vbl_payload;
   for (auto const &vb : resp.varbinds) {
      std::vector<uint8_t> vb_payload;
      encode_oid(vb.oid, vb_payload);
      switch (vb.type) {
         case MockVarbind::Type::Integer:
            encode_integer(vb.int_val, vb_payload);
            break;
         case MockVarbind::Type::OctetString: {
            std::vector<uint8_t> s(vb.str_val.begin(), vb.str_val.end());
            wrap_tlv(0x04, s, vb_payload);
            break;
         }
         case MockVarbind::Type::Oid:
            encode_oid(vb.oid_val, vb_payload);
            break;
         case MockVarbind::Type::Null:
            vb_payload.push_back(0x05);
            vb_payload.push_back(0x00);
            break;
         case MockVarbind::Type::NoSuchObject:
         case MockVarbind::Type::NoSuchInstance:
         case MockVarbind::Type::EndOfMibView:
            vb_payload.push_back(static_cast<uint8_t>(vb.type));
            vb_payload.push_back(0x00);
            break;
      }
      wrap_tlv(0x30, vb_payload, vbl_payload);
   }

   std::vector<uint8_t> pdu_payload;
   encode_integer(req.request_id, pdu_payload);
   encode_integer(resp.error_status, pdu_payload);
   encode_integer(resp.error_index, pdu_payload);
   wrap_tlv(0x30, vbl_payload, pdu_payload);

   std::vector<uint8_t> msg_payload;
   encode_integer(req.version, msg_payload);
   std::vector<uint8_t> comm(req.community.begin(), req.community.end());
   wrap_tlv(0x04, comm, msg_payload);
   wrap_tlv(0xA2, pdu_payload, msg_payload);

   std::vector<uint8_t> packet;
   wrap_tlv(0x30, msg_payload, packet);
   return packet;
}

class MockSnmpUdpServer {
  public:
   using Handler = std::function<MockResponse(MockRequest const &)>;

   explicit MockSnmpUdpServer(Handler handler) : handler_(std::move(handler)) {
      fd_ = socket(AF_INET, SOCK_DGRAM, 0);
      sockaddr_in addr{};
      addr.sin_family = AF_INET;
      addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
      addr.sin_port = 0;
      bind(fd_, reinterpret_cast<sockaddr *>(&addr), sizeof(addr));

      socklen_t addr_len = sizeof(addr);
      getsockname(fd_, reinterpret_cast<sockaddr *>(&addr), &addr_len);
      port_ = ntohs(addr.sin_port);

      timeval tv{};
      tv.tv_sec = 0;
      tv.tv_usec = 50000;
      setsockopt(fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

      running_.store(true);
      thread_ = std::thread([this]() { serve(); });
   }

   ~MockSnmpUdpServer() {
      running_.store(false);
      if (thread_.joinable()) {
         thread_.join();
      }
      if (fd_ >= 0) {
         close(fd_);
      }
   }

   std::string endpoint() const { return "127.0.0.1:" + std::to_string(port_); }

  private:
   void serve() {
      uint8_t buf[4096];
      while (running_.load()) {
         sockaddr_in client{};
         socklen_t client_len = sizeof(client);
         ssize_t n =
             recvfrom(fd_, buf, sizeof(buf), 0, reinterpret_cast<sockaddr *>(&client), &client_len);
         if (n <= 0) {
            continue;
         }
         MockRequest req;
         if (!decode_snmp_request(buf, static_cast<size_t>(n), req)) {
            continue;
         }
         MockResponse resp = handler_(req);
         if (resp.drop) {
            continue;
         }
         std::vector<uint8_t> pkt = encode_snmp_response(req, resp);
         sendto(fd_, pkt.data(), pkt.size(), 0, reinterpret_cast<sockaddr const *>(&client),
                client_len);
      }
   }

   int fd_ = -1;
   uint16_t port_ = 0;
   std::atomic<bool> running_{false};
   std::thread thread_;
   Handler handler_;
};

std::vector<uint32_t> const kHrStorageIndex = {1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 1};
std::vector<uint32_t> const kHrStorageDescr = {1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 3};
std::vector<uint32_t> const kHrStorageUnits = {1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 4};
std::vector<uint32_t> const kHrStorageSize = {1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 5};
std::vector<uint32_t> const kHrStorageUsed = {1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 6};

std::vector<uint32_t> const kDskIndex = {1, 3, 6, 1, 4, 1, 2021, 9, 1, 1};
std::vector<uint32_t> const kDskPath = {1, 3, 6, 1, 4, 1, 2021, 9, 1, 2};
std::vector<uint32_t> const kDskTotal = {1, 3, 6, 1, 4, 1, 2021, 9, 1, 6};
std::vector<uint32_t> const kDskUsed = {1, 3, 6, 1, 4, 1, 2021, 9, 1, 8};

std::vector<uint32_t> with_index(std::vector<uint32_t> base, uint32_t idx) {
   base.push_back(idx);
   return base;
}

} // namespace

class SnmpDfTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpDfTest, TestInvalidCOptionThrowsParseError) {
   std::vector<std::string> args = {"-CZ", "-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_invalid_c"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestInvalidOptionThrowsParseError) {
   std::vector<std::string> args = {"-Z", "-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_invalid_opt"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestHelpThrowsParseError) {
   std::vector<std::string> args = {"-h"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_help"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestVersionThrowsParseError) {
   std::vector<std::string> args = {"-V"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_version"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestMissingHostThrowsParseError) {
   std::vector<std::string> args = {};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_missing_host"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestExtraArgumentThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "extra_arg"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_extra_arg"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestTimeoutThrowsTimeoutError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public",         "-t",
                                    "1",  "-r", "0",  "127.0.0.1:19999"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_timeout"), TimeoutErrorBase);
}

TEST_F(SnmpDfTest, TestInvalidHostnameThrows) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-t", "1", "-r", "0", "nonexistent.invalid.host.example:161"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_bad_host"), GenericErrorBase);
}

TEST_F(SnmpDfTest, TestLiveSnmpdfDefault) {
   if (!is_test_snmpd_available()) {
      GTEST_SKIP() << "Test snmpd not running on 127.0.0.1:11161";
   }
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};
   auto result = snmpdf(args, "testing_snmpdf_default");
   ASSERT_GE(result.size(), 2u);
   EXPECT_NE(result[0].find("Description"), std::string::npos);
   EXPECT_NE(result[0].find("Size (kB)"), std::string::npos);
   EXPECT_NE(result[0].find("Used%"), std::string::npos);
}

TEST_F(SnmpDfTest, TestLiveSnmpdfHumanBinary) {
   if (!is_test_snmpd_available()) {
      GTEST_SKIP() << "Test snmpd not running on 127.0.0.1:11161";
   }
   std::vector<std::string> args = {"-Ch", "-v", "2c", "-c", "public", "localhost:11161"};
   auto result = snmpdf(args, "testing_snmpdf_human_binary");
   ASSERT_GE(result.size(), 2u);
   EXPECT_NE(result[0].find("Description"), std::string::npos);
   EXPECT_NE(result[0].find("Size"), std::string::npos);
   EXPECT_EQ(result[0].find("Size (kB)"), std::string::npos);
}

TEST_F(SnmpDfTest, TestLiveSnmpdfHumanSI) {
   if (!is_test_snmpd_available()) {
      GTEST_SKIP() << "Test snmpd not running on 127.0.0.1:11161";
   }
   std::vector<std::string> args = {"-CH", "-v", "2c", "-c", "public", "localhost:11161"};
   auto result = snmpdf(args, "testing_snmpdf_human_si");
   ASSERT_GE(result.size(), 2u);
   EXPECT_NE(result[0].find("Description"), std::string::npos);
   EXPECT_NE(result[0].find("Size"), std::string::npos);
}

TEST_F(SnmpDfTest, TestMockHrStorageDefaultAndHumanScales) {
   struct StorageEntry {
      uint32_t idx;
      std::string descr;
      int64_t units;
      int64_t size;
      int64_t used;
   };
   std::vector<StorageEntry> entries = {
       {1, "/kb", 1024, 500, 100},
       {2, "/mb", 1024, 2000, 1000},
       {3, "/gb", 1024, 2000000, 500000},
       {4, "/tb", 1048576, 2000000, 500000},
       {5, "/pb", 1073741824, 2000000, 500000},
       {6, "", 0, 0, 0},
       {7, std::string(5000, 'x'), 1024, 100, 50},
   };

   MockSnmpUdpServer server([&](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      if (req.oids.empty()) {
         return resp;
      }
      if (req.pdu_type == 0xA1) { // GETNEXT
         auto const &oid = req.oids[0];
         if (oid == kHrStorageIndex) {
            resp.varbinds.push_back({with_index(kHrStorageIndex, entries[0].idx),
                                     MockVarbind::Type::Integer,
                                     entries[0].idx,
                                     "",
                                     {}});
            return resp;
         }
         if (oid.size() == kHrStorageIndex.size() + 1 &&
             std::equal(kHrStorageIndex.begin(), kHrStorageIndex.end(), oid.begin())) {
            uint32_t cur = oid.back();
            for (size_t i = 0; i + 1 < entries.size(); ++i) {
               if (entries[i].idx == cur) {
                  resp.varbinds.push_back({with_index(kHrStorageIndex, entries[i + 1].idx),
                                           MockVarbind::Type::Integer,
                                           entries[i + 1].idx,
                                           "",
                                           {}});
                  return resp;
               }
            }
            resp.varbinds.push_back({oid, MockVarbind::Type::EndOfMibView, 0, "", {}});
            return resp;
         }
      } else if (req.pdu_type == 0xA0 && req.oids.size() == 4) { // GET
         uint32_t idx = req.oids[0].back();
         for (auto const &e : entries) {
            if (e.idx == idx) {
               resp.varbinds.push_back(
                   {req.oids[0], MockVarbind::Type::OctetString, 0, e.descr, {}});
               resp.varbinds.push_back({req.oids[1], MockVarbind::Type::Integer, e.units, "", {}});
               resp.varbinds.push_back({req.oids[2], MockVarbind::Type::Integer, e.size, "", {}});
               resp.varbinds.push_back({req.oids[3], MockVarbind::Type::Integer, e.used, "", {}});
               return resp;
            }
         }
      }
      return resp;
   });

   auto res_default =
       snmpdf({"-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_mock_default");
   ASSERT_EQ(res_default.size(), 8u);
   EXPECT_NE(res_default[0].find("Size (kB)"), std::string::npos);

   auto res_ch =
       snmpdf({"-Ch", "-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_mock_ch");
   ASSERT_EQ(res_ch.size(), 8u);
   EXPECT_NE(res_ch[1].find("kB"), std::string::npos);
   EXPECT_NE(res_ch[2].find("MiB"), std::string::npos);
   EXPECT_NE(res_ch[3].find("GiB"), std::string::npos);
   EXPECT_NE(res_ch[4].find("TiB"), std::string::npos);
   EXPECT_NE(res_ch[5].find("PiB"), std::string::npos);

   auto res_cH =
       snmpdf({"-CH", "-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_mock_cH");
   ASSERT_EQ(res_cH.size(), 8u);
   EXPECT_NE(res_cH[2].find("MB"), std::string::npos);
   EXPECT_NE(res_cH[3].find("GB"), std::string::npos);
   EXPECT_NE(res_cH[4].find("TB"), std::string::npos);
   EXPECT_NE(res_cH[5].find("PB"), std::string::npos);
}

TEST_F(SnmpDfTest, TestMockHrStorageMissingVars) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      auto const &oid = req.oids[0];
      if (req.pdu_type == 0xA1) {
         if (oid == kHrStorageIndex) {
            resp.varbinds.push_back(
                {with_index(kHrStorageIndex, 1), MockVarbind::Type::Integer, 1, "", {}});
         } else if (oid.size() == kHrStorageIndex.size() + 1 && oid.back() < 5) {
            uint32_t next_idx = oid.back() + 1;
            resp.varbinds.push_back({with_index(kHrStorageIndex, next_idx),
                                     MockVarbind::Type::Integer,
                                     next_idx,
                                     "",
                                     {}});
         } else {
            resp.varbinds.push_back({oid, MockVarbind::Type::EndOfMibView, 0, "", {}});
         }
         return resp;
      }
      uint32_t idx = oid.back();
      resp.varbinds.push_back(
          {req.oids[0],
           idx == 1 ? MockVarbind::Type::NoSuchInstance : MockVarbind::Type::OctetString,
           0,
           "/ok",
           {}});
      resp.varbinds.push_back(
          {req.oids[1],
           idx == 2 ? MockVarbind::Type::NoSuchObject : MockVarbind::Type::Integer,
           1024,
           "",
           {}});
      resp.varbinds.push_back(
          {req.oids[2],
           idx == 3 ? MockVarbind::Type::NoSuchInstance : MockVarbind::Type::Integer,
           100,
           "",
           {}});
      resp.varbinds.push_back(
          {req.oids[3],
           idx == 4 ? MockVarbind::Type::NoSuchObject : MockVarbind::Type::Integer,
           50,
           "",
           {}});
      return resp;
   });

   auto res =
       snmpdf({"-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_missing_vars");
   ASSERT_EQ(res.size(), 2u);
   EXPECT_NE(res[1].find("/ok"), std::string::npos);
}

TEST_F(SnmpDfTest, TestMockHrStorageGetTimeout) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      if (req.pdu_type == 0xA1) {
         if (req.oids[0] == kHrStorageIndex) {
            resp.varbinds.push_back(
                {with_index(kHrStorageIndex, 1), MockVarbind::Type::Integer, 1, "", {}});
         } else {
            resp.varbinds.push_back({req.oids[0], MockVarbind::Type::EndOfMibView, 0, "", {}});
         }
         return resp;
      }
      resp.drop = true;
      return resp;
   });

   EXPECT_THROW(snmpdf({"-v", "2c", "-c", "public", "-t", "1", "-r", "0", server.endpoint()},
                       "testing_snmpdf_hr_get_timeout"),
                TimeoutErrorBase);
}

TEST_F(SnmpDfTest, TestMockCollectPacketError) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      resp.error_status = 5; // SNMP_ERR_GENERR
      resp.error_index = 1;
      resp.varbinds.push_back({req.oids[0], MockVarbind::Type::Null, 0, "", {}});
      return resp;
   });

   EXPECT_THROW(
       snmpdf({"-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_collect_err"),
       PacketErrorBase);
}

TEST_F(SnmpDfTest, TestMockNoPartitionsThrowsGenericError) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      resp.varbinds.push_back({req.oids[0], MockVarbind::Type::NoSuchInstance, 0, "", {}});
      return resp;
   });

   EXPECT_THROW(
       snmpdf({"-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_no_partitions"),
       GenericErrorBase);
}

TEST_F(SnmpDfTest, TestMockUcdDskDefaultHumanAndFallback) {
   struct DskEntry {
      uint32_t idx;
      std::string path;
      int64_t total;
      int64_t used;
   };
   std::vector<DskEntry> entries = {
       {1, "/", 500, 100},
       {2, "/big", 2000000, 500000},
       {3, "", 0, 0},
       {4, std::string(5000, 'y'), 1024, 512},
   };

   MockSnmpUdpServer server([&](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      auto const &oid = req.oids[0];
      if (req.pdu_type == 0xA1) {
         if (oid == kHrStorageIndex) {
            // Return out-of-subtree OID to exercise snmp_oid_compare != 0 and fallback to dskIndex.
            resp.varbinds.push_back(
                {with_index(kHrStorageDescr, 1), MockVarbind::Type::OctetString, 0, "x", {}});
            return resp;
         }
         if (oid == kDskIndex) {
            resp.varbinds.push_back({with_index(kDskIndex, entries[0].idx),
                                     MockVarbind::Type::Integer,
                                     entries[0].idx,
                                     "",
                                     {}});
            return resp;
         }
         if (oid.size() == kDskIndex.size() + 1 &&
             std::equal(kDskIndex.begin(), kDskIndex.end(), oid.begin())) {
            uint32_t cur = oid.back();
            for (size_t i = 0; i + 1 < entries.size(); ++i) {
               if (entries[i].idx == cur) {
                  resp.varbinds.push_back({with_index(kDskIndex, entries[i + 1].idx),
                                           MockVarbind::Type::Integer,
                                           entries[i + 1].idx,
                                           "",
                                           {}});
                  return resp;
               }
            }
            resp.varbinds.push_back({oid, MockVarbind::Type::EndOfMibView, 0, "", {}});
            return resp;
         }
      } else if (req.pdu_type == 0xA0 && req.oids.size() == 3) {
         uint32_t idx = oid.back();
         for (auto const &e : entries) {
            if (e.idx == idx) {
               resp.varbinds.push_back(
                   {req.oids[0], MockVarbind::Type::OctetString, 0, e.path, {}});
               resp.varbinds.push_back({req.oids[1], MockVarbind::Type::Integer, e.total, "", {}});
               resp.varbinds.push_back({req.oids[2], MockVarbind::Type::Integer, e.used, "", {}});
               return resp;
            }
         }
      }
      return resp;
   });

   auto res_fallback =
       snmpdf({"-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_dsk_fallback");
   ASSERT_EQ(res_fallback.size(), 5u);

   auto res_cu_ch = snmpdf({"-Cu", "-Ch", "-v", "2c", "-c", "public", server.endpoint()},
                           "testing_snmpdf_dsk_ch");
   ASSERT_EQ(res_cu_ch.size(), 5u);
   EXPECT_NE(res_cu_ch[1].find("kB"), std::string::npos);
   EXPECT_NE(res_cu_ch[2].find("GiB"), std::string::npos);
}

TEST_F(SnmpDfTest, TestMockUcdDskMissingVars) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      auto const &oid = req.oids[0];
      if (req.pdu_type == 0xA1) {
         if (oid == kDskIndex) {
            resp.varbinds.push_back(
                {with_index(kDskIndex, 1), MockVarbind::Type::Integer, 1, "", {}});
         } else if (oid.size() == kDskIndex.size() + 1 && oid.back() < 4) {
            uint32_t next_idx = oid.back() + 1;
            resp.varbinds.push_back(
                {with_index(kDskIndex, next_idx), MockVarbind::Type::Integer, next_idx, "", {}});
         } else {
            resp.varbinds.push_back({oid, MockVarbind::Type::EndOfMibView, 0, "", {}});
         }
         return resp;
      }
      uint32_t idx = oid.back();
      resp.varbinds.push_back(
          {req.oids[0],
           idx == 1 ? MockVarbind::Type::NoSuchInstance : MockVarbind::Type::OctetString,
           0,
           "/dsk_ok",
           {}});
      resp.varbinds.push_back(
          {req.oids[1],
           idx == 2 ? MockVarbind::Type::NoSuchObject : MockVarbind::Type::Integer,
           100,
           "",
           {}});
      resp.varbinds.push_back(
          {req.oids[2],
           idx == 3 ? MockVarbind::Type::NoSuchInstance : MockVarbind::Type::Integer,
           50,
           "",
           {}});
      return resp;
   });

   auto res =
       snmpdf({"-Cu", "-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_dsk_missing");
   ASSERT_EQ(res.size(), 2u);
   EXPECT_NE(res[1].find("/dsk_ok"), std::string::npos);
}

TEST_F(SnmpDfTest, TestMockUcdDskGetTimeout) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      if (req.pdu_type == 0xA1) {
         if (req.oids[0] == kDskIndex) {
            resp.varbinds.push_back(
                {with_index(kDskIndex, 1), MockVarbind::Type::Integer, 1, "", {}});
         } else {
            resp.varbinds.push_back({req.oids[0], MockVarbind::Type::EndOfMibView, 0, "", {}});
         }
         return resp;
      }
      resp.drop = true;
      return resp;
   });

   EXPECT_THROW(snmpdf({"-Cu", "-v", "2c", "-c", "public", "-t", "1", "-r", "0", server.endpoint()},
                       "testing_snmpdf_dsk_get_timeout"),
                TimeoutErrorBase);
}

TEST_F(SnmpDfTest, TestMockCollectMidWalkErrorFreesVarbinds) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      if (req.pdu_type == 0xA1) {
         if (req.oids[0] == kHrStorageIndex) {
            resp.varbinds.push_back(
                {with_index(kHrStorageIndex, 1), MockVarbind::Type::Integer, 1, "", {}});
         } else {
            resp.error_status = 5;
            resp.error_index = 1;
            resp.varbinds.push_back({req.oids[0], MockVarbind::Type::Null, 0, "", {}});
         }
      }
      return resp;
   });

   EXPECT_THROW(
       snmpdf({"-v", "2c", "-c", "public", server.endpoint()}, "testing_snmpdf_mid_walk_err"),
       PacketErrorBase);
}

TEST_F(SnmpDfTest, TestMockOidOverflowThrowsGenericError) {
   MockSnmpUdpServer server([](MockRequest const &req) -> MockResponse {
      MockResponse resp;
      if (req.pdu_type == 0xA1) {
         if (req.oids[0] == kHrStorageIndex) {
            std::vector<uint32_t> long_oid = kHrStorageIndex;
            for (uint32_t i = 0; i < 118; ++i) {
               long_oid.push_back(1);
            }
            resp.varbinds.push_back({long_oid, MockVarbind::Type::Integer, 1, "", {}});
         } else {
            resp.varbinds.push_back({req.oids[0], MockVarbind::Type::EndOfMibView, 0, "", {}});
         }
      } else {
         resp.varbinds.push_back({req.oids[0], MockVarbind::Type::EndOfMibView, 0, "", {}});
      }
      return resp;
   });

   EXPECT_THROW(snmpdf({"-v", "2c", "-c", "public", "-t", "1", "-r", "0", server.endpoint()},
                       "testing_snmpdf_oid_overflow"),
                GenericErrorBase);
}
