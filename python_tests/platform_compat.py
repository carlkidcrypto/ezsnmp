def is_des_supported() -> bool:
    """
    Check if DES is supported on the current platform.
    DES is not supported on AlmaLinux 10 and later versions."""
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read().lower()
            if 'almalinux' in os_info:
                for line in os_info.split('\n'):
                    if line.startswith('version_id='):
                        version = line.split('=')[1].strip('"\'')
                        major_version = int(version.split('.')[0])
                        if major_version >= 10:
                            return False
    except Exception:
        pass
    return True
