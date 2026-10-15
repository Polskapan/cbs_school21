rule Malware_C_file3
{
    strings:
    $hex_marker = { 90 90 90 ca fe ba be 4d  61 6c 77 61 72 65 5f 43 5f 53 69 67 6e 61 74 75  72 65 0a }

        $str_marker = "Malware_C_Signature"

    condition:
        $hex_marker and $str_marker
}
