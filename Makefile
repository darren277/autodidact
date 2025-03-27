include .env

g:
	gunicorn sse:app --worker-class gevent --bind $(BIND_IP):$(BIND_PORT)

w:
	waitress-serve --listen=*:$(BIND_PORT) wsgi:app

w2:
	waitress-serve --host=127.0.0.1 --port=8000 --asyncore-loop-timeout=3600 --connection-limit=100 wsgi:app

create:
	python manage.py create

drop:
	python manage.py drop


# Makefile for AWS Cognito deployment on Windows
# Requires: AWS CLI, Make for Windows (GnuWin32, or via Git Bash, or WSL)

# Output file
CONFIG_FILE = config.py

# Default target
.PHONY: deploy
deploy: deploy-stack get-outputs create-config

# Deploy CloudFormation stack
.PHONY: deploy-stack
deploy-stack:
	@echo "Deploying CloudFormation stack..."
	aws cloudformation deploy \
		--template-file $(TEMPLATE_FILE) \
		--stack-name $(STACK_NAME) \
		--parameter-overrides \
			AppName=$(APP_NAME) \
			GoogleClientId=$(GOOGLE_CLIENT_ID) \
			GoogleClientSecret=$(GOOGLE_CLIENT_SECRET) \
			CallbackURL=$(CALLBACK_URL) \
		--capabilities CAPABILITY_IAM \
		--region $(AWS_REGION)

# Get stack outputs
.PHONY: get-outputs
get-outputs:
	@echo "Getting CloudFormation stack outputs..."
	$(eval USER_POOL_ID := $(shell aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query "Stacks[0].Outputs[?ExportName=='$(STACK_NAME)-UserPoolId'].OutputValue" --output text --region $(AWS_REGION)))
	$(eval USER_POOL_CLIENT_ID := $(shell aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query "Stacks[0].Outputs[?ExportName=='$(STACK_NAME)-UserPoolClientId'].OutputValue" --output text --region $(AWS_REGION)))
	$(eval COGNITO_DOMAIN := $(shell aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query "Stacks[0].Outputs[?ExportName=='$(STACK_NAME)-CognitoDomain'].OutputValue" --output text --region $(AWS_REGION)))

	@echo "Getting User Pool Client Secret..."
	$(eval USER_POOL_CLIENT_SECRET := $(shell aws cognito-idp describe-user-pool-client --user-pool-id $(USER_POOL_ID) --client-id $(USER_POOL_CLIENT_ID) --query "UserPoolClient.ClientSecret" --output text --region $(AWS_REGION)))

	@echo "----------------------------------------"
	@echo "Cognito Configuration:"
	@echo "----------------------------------------"
	@echo "USER_POOL_ID=$(USER_POOL_ID)"
	@echo "USER_POOL_CLIENT_ID=$(USER_POOL_CLIENT_ID)"
	@echo "USER_POOL_CLIENT_SECRET=$(USER_POOL_CLIENT_SECRET)"
	@echo "COGNITO_DOMAIN=$(COGNITO_DOMAIN)"
	@echo "----------------------------------------"

# Create configuration file
.PHONY: create-config
create-config:
	@echo "Generating config file for Flask app..."
	@echo "# AWS Cognito Configuration" > $(CONFIG_FILE)
	@echo "AWS_REGION = '$(AWS_REGION)'" >> $(CONFIG_FILE)
	@echo "COGNITO_DOMAIN = '$(COGNITO_DOMAIN)'" >> $(CONFIG_FILE)
	@echo "USER_POOL_ID = '$(USER_POOL_ID)'" >> $(CONFIG_FILE)
	@echo "CLIENT_ID = '$(USER_POOL_CLIENT_ID)'" >> $(CONFIG_FILE)
	@echo "CLIENT_SECRET = '$(USER_POOL_CLIENT_SECRET)'" >> $(CONFIG_FILE)
	@echo "REDIRECT_URI = '$(CALLBACK_URL)'" >> $(CONFIG_FILE)
	@echo "Configuration file ($(CONFIG_FILE)) created successfully!"

# Delete the CloudFormation stack
.PHONY: clean
clean:
	@echo "Deleting CloudFormation stack..."
	aws cloudformation delete-stack --stack-name $(STACK_NAME) --region $(AWS_REGION)
	@echo "Waiting for stack deletion to complete..."
	aws cloudformation wait stack-delete-complete --stack-name $(STACK_NAME) --region $(AWS_REGION)
	@echo "Stack deleted successfully!"
	@if exist $(CONFIG_FILE) del $(CONFIG_FILE)

# Show help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  deploy        - Deploy stack and create config file"
	@echo "  deploy-stack  - Deploy the CloudFormation stack"
	@echo "  get-outputs   - Get and display stack outputs"
	@echo "  create-config - Create Flask config file"
	@echo "  clean         - Delete the CloudFormation stack"
	@echo "  help          - Show this help message"
	@echo ""
	@echo "Before running, edit the Makefile to set your:"
	@echo "- AWS region"
	@echo "- Google OAuth credentials"
	@echo "- App name and callback URL"
