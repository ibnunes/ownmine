# Asks a yes/no prompt to the user.
# Args:
#    $1   Prompt
function confirm() {
    echo "$1 (y/N) "
    read response
    return $([[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]])
}
