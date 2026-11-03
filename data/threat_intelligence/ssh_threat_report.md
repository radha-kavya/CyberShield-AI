# SSH Threat Intelligence Report

## Overview
Secure Shell (SSH) is commonly used for remote system administration. Its default network port is 22.

## Common Threat Patterns

### Brute Force Attacks
Attackers may attempt multiple username and password combinations to gain unauthorized access.

### Repeated Authentication Failures
A large number of failed SSH login attempts from the same source IP may indicate suspicious activity.

### Unauthorized Access
Unexpected SSH connections should be reviewed to determine whether they originate from authorized systems.

## Detection Recommendations
- Monitor repeated failed SSH login attempts.
- Identify source IP addresses.
- Review timestamps and authentication records.
- Check whether the source IP is authorized.
- Correlate network events with login logs.

## Defensive Recommendations
- Use strong passwords.
- Enable multi-factor authentication where supported.
- Restrict SSH access to trusted systems.
- Use key-based authentication.
- Monitor SSH authentication logs.

## Investigation Note
Repeated SSH access attempts are indicators that require investigation. They do not independently prove a successful cyberattack.