rule Malware_B_file2
{
    strings:
        $hex_marker = { 90 90 90 ba ad f0 0d 4d  61 6c 77 61 72 65 5f 42 5f 53 69 67 6e 61 74 75 72 65 0a }

        $str_marker = "Malware_B_Signature"

    condition:
        filesize == 512027 and
        $hex_marker and
        $str_marker
}
