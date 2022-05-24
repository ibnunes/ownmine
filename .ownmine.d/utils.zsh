function confirm() {
    echo "$1 (y/N) "
    read response
    return $([[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]])
}