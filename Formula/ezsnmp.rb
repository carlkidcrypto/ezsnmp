class Ezsnmp < Formula
  desc "Blazingly fast Python SNMP library based on Net-SNMP"
  homepage "https://github.com/carlkidcrypto/ezsnmp"
  url "https://github.com/carlkidcrypto/ezsnmp/archive/refs/tags/V2.5.0.tar.gz"
  sha256 "1b00df023252400b110c2b461ca0023ec7f9c5aa98d8473589519f56062eed9d"
  license "BSD-3-Clause"
  head "https://github.com/carlkidcrypto/ezsnmp.git", branch: "main"

  resource "net-snmp" do
    url "https://github.com/net-snmp/net-snmp/archive/refs/tags/v5.10.pre2.tar.gz"
    sha256 "6bce4ef368db15ad0f400330d5a1433009d63f0a98ca8b2eca0f87abd3469bd6"
  end

  depends_on "swig" => :build
  depends_on "openssl@3"

  on_arm do
    depends_on "autoconf" => :build
    depends_on "automake" => :build
    depends_on "libtool" => :build
  end

  def find_python3
    candidates = ["python3"] + Dir["#{HOMEBREW_PREFIX}/opt/python@*/bin/python3"].sort.reverse
    candidates.find { |candidate| File.executable?(candidate) } || "python3"
  end

  def install
    python3 = find_python3
    python_version = Language::Python.major_minor_version(python3)
    default_mibs = %w[
      IP-MIB IF-MIB TCP-MIB UDP-MIB SNMPv2-MIB RFC1213-MIB NOTIFICATION-LOG-MIB
      DISMAN-EVENT-MIB DISMAN-SCHEDULE-MIB HOST-RESOURCES-MIB HOST-RESOURCES-TYPES
      UCD-SNMP-MIB UCD-DEMO-MIB SNMP-TARGET-MIB NET-SNMP-AGENT-MIB NET-SNMP-EXTEND-MIB
      SNMP-FRAMEWORK-MIB SNMP-MPD-MIB SNMP-USER-BASED-SM-MIB
      SNMP-VIEW-BASED-ACM-MIB SNMP-COMMUNITY-MIB NET-SNMP-VACM-MIB
    ].join(":")

    openssl = Formula["openssl@3"]
    ENV.append "LDFLAGS", "-L#{openssl.opt_lib}"
    ENV.append "CPPFLAGS", "-I#{openssl.opt_include}"

    resource("net-snmp").stage do
      system "autoreconf", "--force", "--install", "--verbose" if Hardware::CPU.arm? && File.file?("configure.ac")
      begin
        system "./configure", "--prefix=#{prefix}",
               "--with-defaults",
               "--with-mibs=#{default_mibs}",
               "--with-mibdirs=$HOME/.snmp/mibs:/usr/share/snmp/mibs:/usr/local/share/snmp/mibs:#{HOMEBREW_PREFIX}/share/snmp/mibs",
               "--enable-shared",
               "--disable-static",
               "--disable-agent",
               "--disable-applications",
               "--disable-manuals",
               "--disable-scripts",
               "--disable-mibs",
               "--disable-embedded-perl",
               "--without-perl-modules",
               "--with-openssl=#{openssl.opt_prefix}",
               "--enable-blumenthal-aes"
      rescue ErrorDuringExecution
        opoo File.readlines("config.log").last(80).join if File.exist?("config.log")
        raise
      end
      system "make", "-j#{ENV.make_jobs}"
      system "make", "install"
    end

    # Build ezsnmp against the Net-SNMP 5.10 copy installed in this formula.
    ENV.prepend_path "PATH", "#{prefix}/bin"
    ENV["EZSNMP_NETSNMP_CONFIG"] = "#{prefix}/bin/net-snmp-config"
    ENV.append "LDFLAGS", "-L#{prefix}/lib"
    ENV.append "CPPFLAGS", "-I#{prefix}/include"

    # A temporary build venv supplies setuptools and wheel without modifying
    # Homebrew Python's global environment.  --no-build-isolation is used so
    # swig is taken from PATH (the Homebrew-managed binary declared above via
    # depends_on "swig" => :build) instead of downloading from PyPI.
    system python3, "-m", "venv", buildpath/"build_venv"
    system buildpath/"build_venv/bin/pip3", "install", "--quiet",
      "setuptools==82.0.0", "wheel==0.46.3"

    # Install the package into this formula's prefix.
    # brew link (run automatically after install) symlinks the contents of
    # lib/pythonX.Y/site-packages into HOMEBREW_PREFIX/lib/pythonX.Y/site-packages,
    # which Homebrew Python includes in sys.path — so `import ezsnmp` works
    # without any additional user configuration.
    system buildpath/"build_venv/bin/pip3", "install",
      "--prefix=#{prefix}",
      "--no-deps",
      "--no-binary=:all:",
      "--no-build-isolation",
      buildpath
  end

  def caveats
    python3 = find_python3
    python_version = Language::Python.major_minor_version(python3)
    site_packages = opt_prefix/"lib/python#{python_version}/site-packages"
    <<~EOS
      ezsnmp has been installed for Homebrew Python #{python_version}.

      After installation, `import ezsnmp` should work immediately in
      Homebrew Python #{python_version}.

      If `import ezsnmp` still fails, add the following to your shell profile
      (~/.zshrc or ~/.bash_profile) and restart your terminal:

        export PYTHONPATH="#{site_packages}:$PYTHONPATH"

    EOS
  end

  test do
    python3 = find_python3
    python_version = Language::Python.major_minor_version(python3)
    assert_match "5.10", shell_output("#{bin}/net-snmp-config --version")
    ENV.prepend_path "PYTHONPATH", "#{opt_prefix}/lib/python#{python_version}/site-packages"
    system python3, "-c", "import ezsnmp"
  end
end
