#!/bin/bash
# List of remaining years to process
years=(1888 1894 1898 1905 1906 1907 1910 1911 1920 1924 1925 1927 1928 1931 1932 1934 1936 1956 1959 1960 1963 1964 1966)
for year in "${years[@]}"; do
    echo "$year"
done
