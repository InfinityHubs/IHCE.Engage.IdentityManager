#!/bin/sh

# ==================================================================================================================== #
# InfinityHubs-Connected-Enterprises.SaasOps.Automate.Builder                                                          #
# ==================================================================================================================== #

set -e  # Exit immediately if a command exits with a non-zero status.

# ==================================================================================================================== #
# Ensure the script has execution permissions                                                                          #
# ==================================================================================================================== #

if [ ! -x "$0" ]; then
  chmod +x "$0"
fi

# ==================================================================================================================== #
# Logging Functions Section                                                                                            #
# ==================================================================================================================== #

# Define log levels as constants
INFO="INFO"
ERROR="ERROR"
SUCCESS="SUCCESS"
UNKNOWN="UNKNOWN"

# Define color codes for log messages (optional for better visibility)
RESET="\033[0m"
GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
BLUE="\033[34m"

# Function to log messages with timestamps and optional colors
log_message() {
    local LOG_LEVEL="$1"
    local MESSAGE="$2"
    local DATE_TIME
    DATE_TIME=$(date "+%Y-%m-%d %H:%M:%S")

    # Determine color based on log level
    local COLOR="$RESET"
    case "$LOG_LEVEL" in
        $INFO)
            COLOR="$BLUE"
            ;;
        $ERROR)
            COLOR="$RED"
            ;;
        $SUCCESS)
            COLOR="$GREEN"
            ;;
        $UNKNOWN)
            COLOR="$YELLOW"
            ;;
    esac

    # Print the log message with color and timestamp
    echo -e "${COLOR}[$LOG_LEVEL] $DATE_TIME - $MESSAGE${RESET}"
}

# Shortcut functions to log specific log levels
log_info() { log_message "$INFO" "$1"; }
log_error() { log_message "$ERROR" "$1"; }
log_success() { log_message "$SUCCESS" "$1"; }
log_unknown() { log_message "$UNKNOWN" "$1"; }

# Draw separator line
draw_line() { echo "------------------------------------------------------------"; }

# Function to check and install curl if not available
do_check_and_install_curl() {
    if ! command -v curl &> /dev/null; then
        log_info "curl not found, installing..."
        apk add --no-cache curl
    else
        log_success "curl is already installed."
    fi
}
# ==================================================================================================================== #
# Context Builder | Fetch and Source The External Executor Script                                                      #
# ==================================================================================================================== #
Automate() {
    local Executor="$1"
    if [ -f "/tmp/build_and_package.sh" ]; then
        # If the build script exists, source it
        . "/tmp/build_and_package.sh"
    else
        echo "_Source  ====> ${_Source}"
        # If the build script doesn't exist, check and install curl if necessary
        do_check_and_install_curl

        echo "Executor: ${Executor}"
        # Fetch the build script using curl
        curl -sSL "${_Builder}/${_Source}/${_Vcs}/Build.And.Package.sh" -o "/tmp/build_and_package.sh" && \

        # Source the script after a successful fetch
        . "/tmp/build_and_package.sh" || \

        # If the fetch fails, log an error and exit
        { log_error "Failed to fetch the build script. Please check the URL and network connection."; exit 1; }
    fi
#    if [ -f "/tmp/executor.sh" ]; then
#        # If the build script exists, source it
#        . "/tmp/executor.sh"
#    else
#        # If the build script doesn't exist, check and install curl if necessary
#        do_check_and_install_curl
#
#        # Fetch the build script using curl
#        curl -sSL "${_Builder}/${_Source}/${_Vcs}/${Executor}" -o "/tmp/${Executor}" && \
#
#        # Source the script after a successful fetch
#        . "/tmp/${Executor}" || \
#
#        # If the fetch fails, log an error and exit
#        { log_error "Failed to fetch the build script. Please check the URL and network connection."; exit 1; }
#    fi
}

# ==================================================================================================================== #
# Dispatch Target Method                                                                                               #
# ==================================================================================================================== #

# Parse and validate command-line arguments
dispatch_target() {
    if [ $# -eq 0 ]; then
        log_error "No command specified. Usage: $0 --Target {Build|Scan|Publish|CleanWorkspace} [--Variables {variables}] [--Secrets {secrets}]"
        exit 1
    fi

    while [ $# -gt 0 ]; do
        case "$1" in
            --Target)
                COMMAND="$2"
                shift 2
                ;;
            --Variables)
                VARIABLES="$2"
                shift 2
                ;;
            --Secrets)
                SECRETS="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                log_error "Usage: $0 --Target {Build|Scan|Publish|CleanWorkspace} [--Variables {variables}] [--Secrets {secrets}]"
                exit 1
                ;;
        esac
    done

    if [ -z "$COMMAND" ]; then
        log_error "No command specified. Usage: $0 --Target {Build|Scan|Publish|CleanWorkspace} [--Variables {variables}] [--Secrets {secrets}]"
        exit 1
    fi
}

# ==================================================================================================================== #
# Main Script Execution                                                                                                 #
# ==================================================================================================================== #

COMMAND=""
VARIABLES=""
SECRETS=""

dispatch_target "$@"
#fetch_and_source

log_info "Executing command: $COMMAND"

# Log Variables and Secrets only if provided
[ -n "$VARIABLES" ] && log_info "Variables: $VARIABLES" || log_info "No Variables provided."
[ -n "$SECRETS" ] && log_info "Secrets: $SECRETS" || log_info "No Secrets provided."


case "$COMMAND" in
    Build)
        Automate "Build.And.Package.sh"
        ;;
    Scan)
        Automate "ContainerImageScan.sh"
        ;;
    Publish)
        Automate "PublishArtifacts.sh"
        ;;
    CleanWorkspace)
        Automate "CleanWorkspace.sh"
        ;;
    *)
        log_error "Invalid command: $COMMAND. Usage: $0 --Target {Build|Scan|Publish|CleanWorkspace}"
        exit 1
        ;;
esac
