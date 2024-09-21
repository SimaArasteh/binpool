#!/bin/bash

csv_file="new_binpool.csv"
search_value="c_cpp_program"


function run_chroot {
    local var="$1"
    local target_folder="$2"
    chroot $target_folder /bin/bash -x <<EOF
    #first_line=$(head -n 1 /etc/apt/sources.list)

    # Append deb-src line to the end of the file
    #echo "$first_line" | sed 's/^deb /deb-src /' >> /etc/apt/sources.list

    apt-get update
    apt-get install -y --force-yes build-essential fakeroot devscripts packaging-dev
    ###################
    mkdir compiled
    cd compiled
    mkdir vulnerable
    mkdir patched

    ###########################for vul ############################
    cd vulnerable
    mkdir debfiles
    mkdir binfiles
    mkdir debfiles/opt0
    mkdir debfiles/opt1
    mkdir debfiles/opt2
    mkdir debfiles/opt3

export var="$var"
dget -u --insecure \$var

for item in ./*; do
   #echo \$item
   if [ -d "\$item" ] && [ "\$item" != "./debfiles" ] && [ "\$item" != "./binfiles" ]; then
        cd \$item
        pwd
        cd /debian/patches
        quilt pop -a
        pwd
        
        export LANG=en_US.UTF-8
        apt build-dep .
        ############## for optimization level 0

        yes '' | DEB_BUILD_OPTIONS='nostrip noopt debug' dpkg-buildpackage -b -uc -us

        pwd
        mv ../*.deb ../debfiles/opt0/
        mv ../*.buildinfo ../debfiles/opt0
        mv ../*.changes ../debfiles/opt0
        ############# for optimization level 1

        export CFLAGS="-O1"
        export CXXFLAGS="-O1"
        export FFLAGS="-O1"
        export DEB_BUILD_OPTIONS="nostrip debug"
        debuild -us -uc
        mv ../*.deb ../debfiles/opt1/
        mv ../*.buildinfo ../debfiles/opt1
        mv ../*.changes ../debfiles/opt1

        ############## for optimization level 2
        export CFLAGS="-O2"
        export CXXFLAGS="-O2"
        export FFLAGS="-O2"
        export DEB_BUILD_OPTIONS="nostrip debug"
        debuild -us -uc
        mv ../*.deb ../debfiles/opt2/
        mv ../*.buildinfo ../debfiles/opt2
        mv ../*.changes ../debfiles/opt2
        ################## for optimization level 3
        export CFLAGS="-O3"
        export CXXFLAGS="-O3"
        export FFLAGS="-O3"
        export DEB_BUILD_OPTIONS="nostrip debug"
        debuild -us -uc
        mv ../*.deb ../debfiles/opt3/
        mv ../*.buildinfo ../debfiles/opt3
        mv ../*.changes ../debfiles/opt3







        break
    fi
done

        #########################################for patched############################################
        cd /compiled/patched
        cd patched
        mkdir debfiles
        mkdir binfiles
        mkdir debfiles/opt0
        mkdir debiles/opt1
        mkdir debfiles/opt2
        mkdir debfiles/opt3

dget -u --insecure \$var

for item in ./*; do
   #echo \$item
   if [ -d "\$item" ] && [ "\$item" != "./debfiles" ] && [ "\$item" != "./binfiles" ]; then
        cd \$item
        pwd
        cd /debian/patches
        quilt push -a
        pwd
        
        export LANG=en_US.UTF-8
        apt build-dep .
        ############## for optimization level 0

        yes '' | DEB_BUILD_OPTIONS='nostrip noopt debug' dpkg-buildpackage -b -uc -us

        pwd
        mv ../*.deb ../debfiles/opt0/
        mv ../*.buildinfo ../debfiles/opt0
        mv ../*.changes ../debfiles/opt0
        ############# for optimization level 1

        export CFLAGS="-O1"
        export CXXFLAGS="-O1"
        export FFLAGS="-O1"
        export DEB_BUILD_OPTIONS="nostrip debug"
        debuild -us -uc
        mv ../*.deb ../debfiles/opt1/
        mv ../*.buildinfo ../debfiles/opt1
        mv ../*.changes ../debfiles/opt1

        ############## for optimization level 2
        export CFLAGS="-O2"
        export CXXFLAGS="-O2"
        export FFLAGS="-O2"
        export DEB_BUILD_OPTIONS="nostrip debug"
        debuild -us -uc
        mv ../*.deb ../debfiles/opt2/
        mv ../*.buildinfo ../debfiles/opt2
        mv ../*.changes ../debfiles/opt2
        ################## for optimization level 3
        export CFLAGS="-O3"
        export CXXFLAGS="-O3"
        export FFLAGS="-O3"
        export DEB_BUILD_OPTIONS="nostrip debug"
        debuild -us -uc
        mv ../*.deb ../debfiles/opt3/
        mv ../*.buildinfo ../debfiles/opt3
        mv ../*.changes ../debfiles/opt3







        break
    fi
done

EOF
}
check_valid_url() { 
    url=$1

    
    # Make a HEAD request to the URL and suppress any output
  response_code=$(curl -sL -w "%{http_code}" "$url" -o /dev/null)

  # Check if the response code is 200, indicating a successful request
  if [ $response_code -eq 200 ]; then
    echo true
  else
    echo false
  fi
  }

create_debian_url() {
  local param_value=("$@")
  delimiter="_"

    # Find the position of the first occurrence of the delimiter
    position=$(awk -F"${delimiter}" '{print length($1)}' <<< "${param_value}")

    # Extract the substrings before and after the delimiter
    substring1="${param_value:0:position}"
    substring2="${param_value:position+1}"

  

  # Return the processed result
  #echo $param_value
  #echo $substring1
  #echo $substring2

  url='https://snapshot.debian.org/package'
  final_url="$url/$substring1/$substring2"
  echo $final_url
}
 crawl_html_page() {
    local url="$1"

    # Make the HTTP request and store the response in a variable
    local response=$(curl -s -L "$url")

    echo "$response"
}



function crawl_webpage {
    # Get the URL from the function argument
    url="$1"

    hrefs=$(wget -qO- "$url" | grep -o -E 'href="[^"]+\.dsc"' | sed 's/href="//;s/"$//')

    echo "$hrefs"

}

create_link(){
  main_url='https://snapshot.debian.org'
  input_string="$1"
  end_substring="pool/"

  # Find the ending position of the substring
  end_pos=$(awk -v str="$input_string" -v end="$end_substring" 'BEGIN{print index(str, end) - 1}')

  # Extract the substring
  extracted_string="${input_string:0:end_pos}"
  
  echo "$main_url$extracted_string"
}

find_debian_realease(){
  url="$1"
  input_year=$(echo $url | grep -oP '\d{4}' | head -n 1)

  
    declare -A debian_releases
  debian_releases=(
    ["etch"]="2007"
    ["lenny"]="2009"
    ["squeeze"]="2011"
    ["wheezy"]="2013"
    ["jessie"]="2015"
    ["stretch"]="2017"
    ["buster"]="2019"
    ["bullseye"]="2021"
  )

  

  # Initialize the closest Debian release and its difference to the input year
  local closest_release=""
  local closest_diff=""

  # Iterate over the Debian releases and find the closest one to the input year
  for release in "${!debian_releases[@]}"; do
    local release_year="${debian_releases[$release]}"

    if (( release_year <= input_year )); then
      local diff=$((input_year - release_year))

      if [[ -z $closest_diff ]] || (( diff < closest_diff )); then
        closest_release=$release
        closest_diff=$diff
      fi
    fi
  done

  # Return the closest Debian release
  echo "$closest_release"
}

install_debian_version() {
    version=$1

    # Check if debootstrap is installed
    if ! command -v debootstrap >/dev/null 2>&1; then
        echo "Debootstrap not found. Installing debootstrap..."
        sudo apt-get update
        sudo apt-get install -y debootstrap
    fi

    # Install the specified Debian version using debootstrap
    echo "Installing Debian version: $version"
    sudo debootstrap $version /mnt/debian-$version http://deb.debian.org/debian

    echo "Installation complete."
}
run_debootstrap() {
  # Check if all arguments are provided
  if [ "$#" -ne 4 ]; then
      echo "You must enter exactly 4 arguments: release_name, target_folder, url, and architecture."
      return 1
  fi

  # Assign arguments to variables
  local release_name="$1"
  local target_folder="/data1/sima/binpool_bins/amd64/""$2"
  local url="$3"
  local architecture="amd64"
  local source_url="$4"

  # Convert https to http in the url
  url=${url/https/http}

  # Run debootstrap with the arguments
  if debootstrap --variant=minbase --arch "$architecture" "$release_name" "$target_folder" "$url"; then
    echo "Debootstrap installation successful."
    run_chroot $source_url $target_folder
  else
    echo "Debootstrap installation failed."
    return 1
  fi
}
# Check if the CSV file exists
if [ ! -f "$csv_file" ]; then
  echo "Error: File '$csv_file' not found."
  exit 1
fi

# Read the CSV file and extract values from column 2 when column 3 matches the search value
# declare an array to store the tuples
declare -a tuples_first
declare -a tuples_second

# read the CSV file and check the 3rd column value
while IFS=, read -r col1 col2 col3 col4
do
  if [[ $col4 == "c_cpp_program" ]]; then
    # if column 3 has value "c_cpp_program", save the values of column 0 and 2
    tuples_first+=("$col1")
    tuples_second+=("$col3")
  fi
done < "$csv_file"

# Print the extracted values from column 2
for index in ${!tuples_first[*]}; do
  #echo $index
  #echo "${tuples_first[$index]}"
  #echo "${tuples_second[$index]}"
  #if [[ "${tuples_second[$index]}" == "miniupnpd_1.8.20140523-4.1%2Bdeb9u1" ]]; then
    target_folder="${tuples_first[$index]}""_index"$index
    
    result=$(create_debian_url "${tuples_second[$index]}")
    echo "Processed result: $result"
    wait_time=2
    sleep $wait_time

    res2=$(check_valid_url "${result[@]}")
    #echo $result
    #echo $res2
    #if the url is valid then crawl the html web page 
    #if [ "$res2" = true ]; then
    sleep $wait_time

    links=$(crawl_webpage "$result")
    #echo $links

    for href in $links; do
      # Check if '/debian/' is present in the href
      if [[ $href == *"/debian/"* ]]; then
          #echo "Found href containing '/debian/': $href"
          main_url='https://snapshot.debian.org'
          source_url=$main_url$href
          debian_snapshot_url=$(create_link "$href")
          
          
          sleep $wait_time
          debian_r=$(find_debian_realease "$debian_snapshot_url")
          echo $debian_snapshot_url
          echo $source_url
          echo $debian_r
          echo $target_folder
          run_debootstrap $debian_r $target_folder $debian_snapshot_url $source_url

        
      fi   
        
        
        
    
    
  done
  #break
  #fi
  
done