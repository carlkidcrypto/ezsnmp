class Ezsnmp < Formula
  desc "Blazingly fast Python SNMP library based on Net-SNMP"
  homepage "https://github.com/carlkidcrypto/ezsnmp"
  url "https://github.com/carlkidcrypto/ezsnmp/archive/refs/tags/v2.4.0.tar.gz"
  sha256 "20a3eb641e77e2acdc8d60364c8b37cdd49220093edd00f2cda87822431c0db8"
  license "BSD-3-Clause"
  head "https://github.com/carlkidcrypto/ezsnmp.git", branch: "main"

  depends_on "swig" => :build
  depends_on "net-snmp"
  depends_on "openssl@3"

  def find_python3
    candidates = ["python3"] + Dir["#{HOMEBREW_PREFIX}/opt/python@*/bin/python3"].sort.reverse
    candidates.find { |candidate| File.executable?(candidate) } || "python3"
  end

  def install
    python3 = find_python3
    python_version = Language::Python.major_minor_version(python3)

    # net-snmp is keg-only; put net-snmp-config on PATH so setup.py can find it
    ENV.prepend_path "PATH", Formula["net-snmp"].opt_bin

    # Point compiler and linker at net-snmp and openssl headers/libs
    ENV.append "LDFLAGS", "-L#{Formula["net-snmp"].opt_lib}"
    ENV.append "LDFLAGS", "-L#{Formula["openssl@3"].opt_lib}"
    ENV.append "CPPFLAGS", "-I#{Formula["net-snmp"].opt_include}"
    ENV.append "CPPFLAGS", "-I#{Formula["openssl@3"].opt_include}"

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
    ENV.prepend_path "PYTHONPATH", "#{opt_prefix}/lib/python#{python_version}/site-packages"
    system python3, "-c", "import ezsnmp"
  end
end
