#!/bin/sh

set -e

# Ensure the script has execution permissions
if [ ! -x "$0" ]; then
  chmod +x "$0"
fi

# Function to return the list of required environment variables
get_required_vars() {
    echo "CI \
    GITHUB_ACTION \
    GITHUB_ACTIONS \
    GITHUB_ACTOR \
    GITHUB_API_URL \
    GITHUB_ENV \
    GITHUB_EVENT_NAME \
    GITHUB_EVENT_PATH \
    GITHUB_JOB \
    GITHUB_OUTPUT \
    GITHUB_PATH \
    GITHUB_REF \
    GITHUB_REF_NAME \
    GITHUB_REF_PROTECTED \
    GITHUB_REF_TYPE \
    GITHUB_REPOSITORY \
    GITHUB_REPOSITORY_OWNER \
    GITHUB_REPOSITORY_OWNER_ID \
    GITHUB_RUN_ATTEMPT \
    GITHUB_RUN_ID \
    GITHUB_RUN_NUMBER \
    GITHUB_SERVER_URL \
    GITHUB_SHA \
    GITHUB_STEP_SUMMARY \
    GITHUB_WORKFLOW \
    GITHUB_WORKSPACE \
    GITHUB_RETENTION_DAYS"
}

# Function to check and install curl if not available
do_check_and_install_curl() {
    if ! command -v curl &> /dev/null; then
        log_info "curl not found, installing..."
        apk add --no-cache curl
    else
        log_success "curl is already installed."
    fi
}

# Function to check and install jq if not available
do_check_and_install_jq() {
    if ! command -v jq &> /dev/null; then
        log_info "jq not found, installing..."
        apk add --no-cache jq
    else
        log_success "jq is already installed."
    fi
}

# Global Variables
ARTIFACTS_DIR="Build-Runner-Artifacts"

# Function to log messages with color
log_info() { echo -e "\033[0;34m$1\033[0m"; } # Blue

log_success() { echo -e "\033[0;32m$1\033[0m"; } # Green

log_warning() { echo -e "\033[0;33m$1\033[0m"; } # Yellow

log_error() { echo -e "\033[0;31m$1\033[0m";  } # Red

# Function to draw a horizontal line
draw_line() { echo -e  "\033[0;34m$1\033[0m"; }

# Function to print the table header (Centralized and bolded)
log_table_header() {
    local header_message="$1"  # Take the message as an argument
    log_info "\033[1m\033[0;34m $header_message \033[0m"
    log_info "------------------------------------------------------------------------------"
}

# Function to print the table footer
log_table_footer() {
    log_info "------------------------------------------------------------------------------"
}

# Function to set up artifacts
prepare_artifacts_volume() {
    # Create the artifacts directory
    mkdir -p "$ARTIFACTS_DIR"
    log_info "Artifacts directory created at: $ARTIFACTS_DIR"
}

# Function to Bootstrap
Bootstrap() {

    log_info "=== Starting Bootstrap ==="

    # Install required tools if not already available
    do_check_and_install_curl
    do_check_and_install_jq

    # Creates the artifacts directory
    prepare_artifacts_volume

    # Fetch the required environment variables dynamically
    REQUIRED_VARS=$(get_required_vars)

    # Initialize an empty JSON object
    JSON_OBJECT="{"

    # Initialize a counter to help avoid the trailing `|` in the last row
    counter=0
    total_vars=$(echo "$REQUIRED_VARS" | wc -w)

    # Print table header
    log_table_header "CI/CD Global Pipeline Variables"

    # Iterate over each required variable and validate
    for VAR in $REQUIRED_VARS; do
    # Use eval to get the value of the variable
    VALUE=$(eval echo \$$VAR)

    if [ -z "$VALUE" ]; then
        log_error "Error: $VAR is not set or empty."
#        exit 1  # Exit if any required variable is not found
    else
        # Append the variable to the JSON object
        JSON_OBJECT="$JSON_OBJECT\"$VAR\": \"$VALUE\","

        # Log the key-value pair in the table without trailing '|'
        if [ $counter -eq $((total_vars - 1)) ]; then
            # For the last variable, print without the trailing '|'
            printf "| %-28s | %-40s \n" "$VAR" "$VALUE"
        else
            # For other variables, print with the trailing '|'
            printf "| %-28s | %-40s \n" "$VAR" "$VALUE"
        fi

        # Increment the counter
        counter=$((counter + 1))
    fi
    done

    # Remove the trailing comma from the JSON object
    JSON_OBJECT=$(echo "$JSON_OBJECT" | sed 's/,$//')

    # Close the JSON object
    JSON_OBJECT="$JSON_OBJECT}"

    # Export the JSON object as a GitLab CI/CD variable
    export GLOBAL_PIPELINE_INFO="$JSON_OBJECT"

    # Print table footer
    log_table_footer \n

    log_info "=== Bootstrap Completed ==="
}

# Function to build the Docker image
BuildAndPackage() {

    log_info "=== Starting Build-and-Package ==="

    # Pre-build cleanup (optional, to remove dangling images)
    log_info "Cleaning up unused Docker resources..."
    docker system prune --force --filter "until=24h"
    draw_line  # Draw line after cleanup operation

    # Set environment-specific variables
    CI_REGISTRY_IMAGE="ghcr.io/${GITHUB_REPOSITORY}"
    CI_PIPELINE_IID="${GITHUB_RUN_NUMBER}"

    # Convert repository name to lowercase for Docker compatibility
    CI_REGISTRY_IMAGE=$(echo "$CI_REGISTRY_IMAGE" | tr '[:upper:]' '[:lower:]')

    # Build Docker image
    log_info "🚀🔨 \033[1mHold tight! Docker build initiated.......\033[0m 🔨🚀\n\n"
    if docker build --pull --no-cache -t "$CI_REGISTRY_IMAGE":"$CI_PIPELINE_IID" .; then
        log_info "\033[1m\033[0;34m CI Docker image built successfully \033[0m"
        log_info "------------------------------------------------------------------------------"
        log_info "| Container Registry Image | $CI_REGISTRY_IMAGE:$CI_PIPELINE_IID"
        log_info "------------------------------------------------------------------------------"
        docker images | grep "$CI_REGISTRY_IMAGE" | grep "$CI_PIPELINE_IID"
        log_info "------------------------------------------------------------------------------"
        log_success "[SUCCESS] 🚀 Hold on, moving on to the next step... ✨"
    else
        log_error "[ERROR] Docker image build failed. Please check the build logs for details and ensure that all necessary files and configurations are in place properly."
        exit 1
    fi
    draw_line  # Draw line after build operation

    # Post-build steps (optional)
    log_info "🔍 Post-build validation in progress..."

    # Validate if the image exists
    if docker inspect "$CI_REGISTRY_IMAGE:$CI_PIPELINE_IID" > /dev/null 2>&1; then
        log_success "✅ [SUCCESS] Image $CI_REGISTRY_IMAGE:$CI_PIPELINE_IID exists."
        docker save "$CI_REGISTRY_IMAGE":"$CI_PIPELINE_IID" > $ARTIFACTS_DIR/pipeline-artifact-"$CI_PIPELINE_IID".tar
        # docker create --name temp_container "$CI_REGISTRY_IMAGE:$CI_PIPELINE_IID"
        # # docker export temp_container | tar -tv | sort -u
        # docker export temp_container > $ARTIFACTS_DIR/automate-ci-builder-temp-container.tar
        # docker rm temp_container
        log_info "\033[1m\033[0;34m Container Artifact Capturing \033[0m"
        log_info "------------------------------------------------------------------------------"
        log_info "| Status   | ✅"
        log_info "------------------------------------------------------------------------------"
        log_success "[SUCCESS] 🚀 Hold on, moving on to the next step... ✨"
    else
        log_error "❌ [ERROR] Post Validation for $CI_REGISTRY_IMAGE:$CI_PIPELINE_IID failed."
        exit 1
    fi

    draw_line  # Draw line after post-build validation

    log_info "=== Build-and-Package Complete ==="
}

# Function to scan the Docker image for vulnerabilities
ContainerImageScan() {
    log_table_header "🔄 Container-Image-Scan"

    # Load the Docker image from the tar file
    IMAGE_TAR="$ARTIFACTS_DIR/pipeline-artifact-$CI_PIPELINE_IID.tar"

    if [ ! -f "$IMAGE_TAR" ]; then
        echo "❌ Tar file not found: $IMAGE_TAR"
        exit 1
    fi

    echo "✅ Found tar file: $IMAGE_TAR"

    echo "🔄 Loading the Docker image from the tar file..."
    if docker load < "$IMAGE_TAR"; then
        echo "✅ Successfully loaded Docker image from $IMAGE_TAR"
    else
        echo "❌ Failed to load Docker image"
        exit 1
    fi

    # Pull the Trivy scanner
    if docker pull aquasec/trivy:latest; then
        echo "✅ Successfully pulled Trivy image"
    else
        echo "❌ Failed to pull Trivy image"
        exit 1
    fi

    # Define the image name (ensure this matches the loaded image)
    IMAGE_NAME="$CI_REGISTRY_IMAGE:$CI_PIPELINE_IID"

    # Check if the image exists locally
    if docker images | grep -q "$CI_REGISTRY_IMAGE"; then
        echo "✅ Image $IMAGE_NAME is available locally."
    else
        echo "❌ Image $IMAGE_NAME not found locally. Exiting."
        exit 1
    fi

    # Verify loaded Docker images
    log_info "🔍 Checking available Docker images..."
    docker images
    draw_line

    # Run the Trivy scan
    echo "🔍 Starting Trivy scan for vulnerabilities..."

    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v $(pwd):/project \
        aquasec/trivy:latest image \
        --ignorefile /project/.trivyignore \
        --format table \
        --exit-code 1 \
        --scanners vuln,secret \
        --show-suppressed \
        --severity CRITICAL,HIGH,MEDIUM \
        "$IMAGE_NAME"

    draw_line  # Draw a separator
    echo "✅ Scan completed successfully"
}

# Function to publish the Docker image to the registry
PublishArtifacts() {

    # Push Docker image to the registry
    log_table_header "🔄 Pushing Docker image to the Github Container Registry..."

    # Set environment-specific variables
    CI_PIPELINE_IID="${GITHUB_RUN_NUMBER}"
    CI_REGISTRY_IMAGE="ghcr.io/${GITHUB_REPOSITORY}"

    # Convert repository name to lowercase for Docker compatibility
    CI_REGISTRY_USER="${GITHUB_ACTOR}"
    CI_REGISTRY_PASSWORD="${GHP_TOKEN}"
    TargetVersion="$SemanticTargetVersion"
    CI_REGISTRY_IMAGE=$(echo "$CI_REGISTRY_IMAGE" | tr '[:upper:]' '[:lower:]')



    # Load the Docker image from the tar file
    IMAGE_TAR="$ARTIFACTS_DIR/pipeline-artifact-$CI_PIPELINE_IID.tar"

    if [ ! -f "$IMAGE_TAR" ]; then
        echo "❌ Tar file not found: $IMAGE_TAR"
        exit 1
    fi

    echo "✅ Found tar file: $IMAGE_TAR"

    echo "🔄 Loading the Docker image from the tar file..."

    if docker load < "$IMAGE_TAR"; then
        echo "✅ Successfully loaded Docker image from $IMAGE_TAR"
        log_table_header "Artifactory Images"
        docker images
        draw_line
        docker tag "$CI_REGISTRY_IMAGE":"$CI_PIPELINE_IID" "$CI_REGISTRY_IMAGE":"$TargetVersion"
        echo "$CI_REGISTRY_PASSWORD" | docker login ghcr.io -u "$CI_REGISTRY_USER" --password-stdin
        if docker --debug push "$CI_REGISTRY_IMAGE":"$TargetVersion"; then
            log_info "\033[1m\033[0;34mCI Publish Artifacts Log Summary \033[0m"
            log_info "------------------------------------------------------------------------------"
            log_info "| Artifact  Image     | $CI_REGISTRY_IMAGE:$CI_PIPELINE_IID"
            log_info "| Published Image     | $CI_REGISTRY_IMAGE:$TargetVersion"
            log_info "| Build Version       | $TargetVersion"
            log_info "------------------------------------------------------------------------------"
            log_success "✅ [SUCCESS] 🚀 Docker image pushed successfully....✨"
        else
            log_error "❌ Docker image push failed. Check detailed logs above for more information."
            exit 1
        fi
    else
        echo "❌ Failed to load Docker image"
        exit 1
    fi
}

CleanWorkspace() {
    rm -rf $ARTIFACTS_DIR
}

# Initialize variables
COMMAND=""
SemanticTargetVersion=""

# Parse arguments
# shellcheck disable=SC3010
while [[ $# -gt 0 ]]; do
    case "$1" in
        --Target)
            COMMAND="$2"
            shift 2
            ;;
        --Version)
            SemanticTargetVersion="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            log_error "Usage: $0 --Target {Build|Scan|Publish|CleanWorkspace} [--Version <version> (required for Publish)]"
            exit 1
            ;;
    esac
done

# Validate the COMMAND
# shellcheck disable=SC3010
if [[ -z "$COMMAND" ]]; then
    log_error "No command specified. Usage: $0 --Target {Build|Scan|Publish|CleanWorkspace} [--Version <version> (required for Publish)]"
    exit 1
fi

# Validate the Version for Publish
# shellcheck disable=SC3010
if [[ "$COMMAND" == "Publish" && -z "$VERSION" ]]; then
    log_error "No version specified for Publish. Usage: $0 --Target Publish --Version <version>"
    exit 1
fi

# Command Dispatcher
case $COMMAND in
    Build)
        Bootstrap
        BuildAndPackage
        ;;
    Scan)
        ContainerImageScan
        ;;
    Publish)
        PublishArtifacts
        ;;
    CleanWorkspace)
        CleanWorkspace
        ;;
    *)
        log_error "Invalid command: $COMMAND. Usage: $0 --Target {Build|Scan|Publish|CleanWorkspace}"
        exit 1
        ;;
esac