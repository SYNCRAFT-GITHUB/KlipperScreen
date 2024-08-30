safe_git_clone() {
    local repo_url="$1"
    local repo_branch="$2"
    local repo_name="$3"

    if [ -z "$repo_branch" ]; then
        git clone --quiet "$repo_url" "$repo_name"
    else
	    git clone --quiet -b "$repo_branch" "$repo_url" "$repo_name"
    fi

    if [ $? -eq 0 ]; then
        echo "Sucessfuly cloned $repo_name"
    else
        echo "Unable to clone $repo_name"
        delete_clones_directory
        exit 1
    fi
}

safe_wget() {
    local url="$1"
    local name="$2"

    wget -q $url
    if [ $? -eq 0 ]; then
        echo "Sucessfuly downloaded $2"
    else
        echo "Download failed for $2"
        delete_clones_directory
        exit 1
    fi
}