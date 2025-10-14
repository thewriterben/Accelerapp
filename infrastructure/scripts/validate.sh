#!/bin/bash
# Validation script for Accelerapp Infrastructure
# This script validates the Terraform configuration and AWS setup

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

validate_terraform() {
    print_info "Validating Terraform configuration..."
    
    cd terraform
    
    # Validate syntax
    if terraform validate; then
        print_success "Terraform configuration is valid"
    else
        print_error "Terraform configuration has errors"
        return 1
    fi
    
    # Format check
    if terraform fmt -check -recursive; then
        print_success "Terraform files are properly formatted"
    else
        print_warning "Some Terraform files need formatting. Run: terraform fmt -recursive"
    fi
    
    cd ..
}

validate_aws() {
    print_info "Validating AWS configuration..."
    
    # Check AWS credentials
    if aws sts get-caller-identity > /dev/null 2>&1; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
        USER_ARN=$(aws sts get-caller-identity --query 'Arn' --output text)
        print_success "AWS credentials are valid"
        print_info "  Account ID: ${ACCOUNT_ID}"
        print_info "  User: ${USER_ARN}"
    else
        print_error "AWS credentials are not configured"
        return 1
    fi
    
    # Check IAM permissions (basic checks)
    print_info "Checking IAM permissions..."
    
    if aws iam list-roles --max-items 1 > /dev/null 2>&1; then
        print_success "IAM read permissions available"
    else
        print_warning "IAM read permissions may be limited"
    fi
    
    if aws ec2 describe-vpcs --max-results 1 > /dev/null 2>&1; then
        print_success "EC2/VPC permissions available"
    else
        print_warning "EC2/VPC permissions may be limited"
    fi
    
    if aws eks list-clusters --max-results 1 > /dev/null 2>&1; then
        print_success "EKS permissions available"
    else
        print_warning "EKS permissions may be limited"
    fi
}

validate_tools() {
    print_info "Validating required tools..."
    
    local all_ok=true
    
    # Check Terraform
    if command -v terraform &> /dev/null; then
        TF_VERSION=$(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)
        print_success "Terraform ${TF_VERSION} found"
    else
        print_error "Terraform not found"
        all_ok=false
    fi
    
    # Check AWS CLI
    if command -v aws &> /dev/null; then
        AWS_VERSION=$(aws --version | cut -d' ' -f1 | cut -d'/' -f2)
        print_success "AWS CLI ${AWS_VERSION} found"
    else
        print_error "AWS CLI not found"
        all_ok=false
    fi
    
    # Check kubectl (optional)
    if command -v kubectl &> /dev/null; then
        K8S_VERSION=$(kubectl version --client --short 2>/dev/null || echo "unknown")
        print_success "kubectl found: ${K8S_VERSION}"
    else
        print_warning "kubectl not found (optional)"
    fi
    
    if [ "$all_ok" = false ]; then
        return 1
    fi
}

validate_structure() {
    print_info "Validating directory structure..."
    
    local required_dirs=(
        "terraform"
        "terraform/modules/vpc"
        "terraform/modules/eks"
        "terraform/modules/iam"
        "terraform/modules/s3"
        "terraform/environments/dev"
        "terraform/environments/staging"
        "terraform/environments/prod"
        "docs"
        "scripts"
    )
    
    local all_ok=true
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_success "Directory exists: ${dir}"
        else
            print_error "Directory missing: ${dir}"
            all_ok=false
        fi
    done
    
    local required_files=(
        "terraform/main.tf"
        "terraform/variables.tf"
        "terraform/outputs.tf"
        "terraform/environments/dev/terraform.tfvars"
        "README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "File exists: ${file}"
        else
            print_error "File missing: ${file}"
            all_ok=false
        fi
    done
    
    if [ "$all_ok" = false ]; then
        return 1
    fi
}

print_summary() {
    echo ""
    print_info "Validation Summary"
    echo "=================="
    echo ""
    echo "Next steps:"
    echo "  1. Review environment configurations in terraform/environments/"
    echo "  2. Initialize Terraform: cd terraform && terraform init"
    echo "  3. Plan deployment: terraform plan -var-file=environments/dev/terraform.tfvars"
    echo "  4. Deploy: terraform apply -var-file=environments/dev/terraform.tfvars"
    echo ""
    print_info "See README.md for detailed deployment instructions"
}

# Main function
main() {
    print_info "Accelerapp Infrastructure Validation"
    echo ""
    
    local exit_code=0
    
    # Run validations
    validate_tools || exit_code=$?
    echo ""
    
    validate_structure || exit_code=$?
    echo ""
    
    validate_aws || exit_code=$?
    echo ""
    
    validate_terraform || exit_code=$?
    echo ""
    
    if [ $exit_code -eq 0 ]; then
        print_success "All validations passed!"
        print_summary
    else
        print_error "Some validations failed. Please fix the issues above."
        exit 1
    fi
}

# Run main
main "$@"
