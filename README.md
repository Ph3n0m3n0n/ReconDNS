# ReconDNS
This AWS Lambda script assumes a specified IAM role across all accounts in an AWS Organization to retrieve and log DNS A records from Route 53 hosted zones in parallel. Used for infrastructure mapping, security auditing and asset inventory. It is designed to be performance driven and provide detailed debugging and logging information.

# AWS Lambda Function: Cross-Account DNS A Record Retriever

This AWS Lambda function assumes a specified IAM role across all accounts in an AWS Organization to retrieve and log DNS A records from Route 53 hosted zones in parallel. The function is designed to be performance-efficient, handle errors gracefully, and provide status updates during execution.

## Features

- **Cross-Account Access:** Automatically assumes a specified IAM role across all AWS accounts in your organization.
- **DNS A Record Retrieval:** Fetches DNS A records from Route 53 hosted zones in each account.
- **Parallel Processing:** Uses multithreading to process multiple accounts simultaneously, enhancing performance.
- **Error Handling:** Includes robust error handling with detailed logging for debugging.
- **Status Updates:** Provides clear status updates without overwhelming logs.

## Prerequisites

Before deploying and running this Lambda function, ensure you have the following:

- **AWS CLI:** Install and configure the AWS CLI on your local machine.
- **AWS IAM Role:** Ensure the role you want to assume (`security-audit-role` in this example) exists in all the target AWS accounts and has the necessary permissions.
- **AWS Lambda Execution Role:** The Lambda function's execution role should have permissions to list accounts in the organization and assume the specified role in each account.

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Ph3n0m3n0n/ReconDNS.git
   cd ReconDNS
   ```

2. **Create and Configure the Lambda Function:**
   - Go to the AWS Management Console and create a new Lambda function.
   - Choose `Python 3.x` as the runtime.
   - Upload the `ReconDNS.py` script to the Lambda function.
   - Set up the execution role with the necessary permissions (e.g., `organizations:ListAccounts`, `sts:AssumeRole`, `route53:ListHostedZones`, `route53:ListResourceRecordSets`).

3. **Environment Variables (Optional):**
   - You can define environment variables in the Lambda function configuration if you need to customize the role name or other parameters.

## Usage

### Deploy the Lambda Function

Once the function is set up, you can deploy and invoke it using the AWS Lambda console or via the AWS CLI.

### Invoking the Function

You can invoke the Lambda function manually or set it up to trigger automatically based on certain events (e.g., changes in Route 53 hosted zones).

### Monitoring and Logs

- **CloudWatch Logs:** The function outputs logs to Amazon CloudWatch, where you can monitor the status updates and review any errors that occur during execution.
- **Status Updates:** The function provides informational messages to track progress and errors in real-time.

### Customization

- **Role Name:** If you need to change the role that the function assumes, modify the `role_name` variable in the `lambda_handler` function.
- **Max Workers:** Adjust the `max_workers` parameter in the `ThreadPoolExecutor` to control the level of parallelism based on your AWS environment and load.

## Example

```python
role_name = "security-audit-role"  # Replace with your actual role name
```

### Return Results

The function returns the list of retrieved DNS A records, including account IDs, domain names, and associated IP addresses.

## Troubleshooting

- **Permissions:** Ensure that the Lambda execution role has the necessary permissions to assume roles in other accounts and access Route 53.
- **Timeouts:** If the function times out, consider adjusting the timeout settings in the Lambda function configuration.
- **Errors in Logs:** Review CloudWatch logs for any `[ERROR]` messages to identify and resolve issues.

## Contributing

If you would like to contribute to this project, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

``` 
