rule Malware_A_file1
{
    strings:
        $hex_marker = { 90 90 90 de ad be ef 4d  61 6c 77 61 72 65 5f 41 5f 53 69 67 6e 61 74 75 72 65 0a }

        $str_marker = "Malware_A_Signature"

    condition:
        $hex_marker and $str_marker
}
