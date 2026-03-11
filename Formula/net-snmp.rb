class NetSnmp < Formula
  desc "Custom Net-SNMP build for EzSnmp testing/development"
  homepage "http://www.net-snmp.org/"
  url "https://downloads.sourceforge.net/project/net-snmp/net-snmp/5.9.5.2/net-snmp-5.9.5.2.tar.gz"
  sha256 "16707719f833184a4b72835dac359ae188123b06b5e42817c00790d7dc1384bf"
  license all_of: ["MIT-CMU", "MIT", "BSD-3-Clause"]
  head "https://github.com/net-snmp/net-snmp.git", branch: "master"

  livecheck do
    url :stable
    regex(%r{url=.*?/net-snmp[._-]v?(\d+(?:\.\d+)+)\.t}i)
  end

  keg_only :provided_by_macos

  depends_on "openssl@3"

  on_arm do
    depends_on "autoconf" => :build
    depends_on "automake" => :build
    depends_on "libtool" => :build
  end

  # Fix -flat_namespace being used on x86_64 Big Sur and later.
  patch do
    url "https://raw.githubusercontent.com/Homebrew/homebrew-core/1cf441a0/Patches/libtool/configure-big_sur.diff"
    sha256 "35acd6aebc19843f1a2b3a63e880baceb0f5278ab1ace661e57a502d9d78c93c"
  end

  def install
    args = [
      "--disable-debugging",
      "--enable-ipv6",
      "--with-defaults",
      "--with-persistent-directory=#{var}/db/net-snmp",
      "--with-logfile=#{var}/log/snmpd.log",
      "--with-mib-modules=host ucd-snmp/diskio",
      "--without-rpm",
      "--without-kmem-usage",
      "--disable-embedded-perl",
      "--without-perl-modules",
      "--with-openssl=#{Formula["openssl@3"].opt_prefix}",
    ]

    on_arm do
      system "autoreconf", "--force", "--install", "--verbose"
    end

    # Work around snmptrapd.c:(.text+0x1e0): undefined reference to `dropauth' on Linux
    ENV.deparallelize if OS.linux?

    system "./configure", *args, *std_configure_args
    system "make"
    system "make", "install"

    (var/"db/net-snmp").mkpath
    (var/"log").mkpath
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/snmpwalk -V 2>&1")
  end
end
