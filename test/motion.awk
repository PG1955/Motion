BEGIN {
}

{
    split($0, items, ',')
    printf("self.config.set('DEF', '%s', '%s')\n", items[1], items[2])
}

END {
}