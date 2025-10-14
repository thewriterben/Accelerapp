#!/bin/bash
# Bootstrap script for Accelerapp Infrastructure

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Main function
main() {
    print_info "Accelerapp Infrastructure Bootstrap"
    
    if [ "$#" -lt 1 ]; then
        print_error "Usage: $0 <environment>"
        exit 1
    fi
    
    ENV=$1
    
    if [[ ! "$ENV" =~ ^(dev|staging|prod)$ ]]; then
        print_error "Invalid environment. Must be dev, staging, or prod"
        exit 1
    fi
    
    print_info "Deploying ${ENV} environment..."
    print_info "See infrastructure/README.md for detailed instructions"
}

main "$@"
