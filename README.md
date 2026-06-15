# Telescope

A web application for managing streaming channels on Amazon Prime Video, built with Flask and PostgreSQL.  
Available at: https://qa-devops-assignment.onrender.com/

## Using the Application

### Browsing Channels

All users (including unauthenticated visitors) can view the channel browser at `/channels`, accessible via the 'Channels' link in the page header.   
The table displays each channel's ID, name, and monthly price. Click any column header to sort the table by that attribute.

### Logging In

Navigate to `/login` via the 'Register/Login' link and enter your credentials. Admin credentials are provided below for viewing purposes.

### Registering an Account

Navigate to `/register` from the login page to create a new account.  
Usernames must be 20 characters or fewer and may only contain letters, numbers, hyphens, and underscores.  
Passwords must be at least 15 characters and may not use a space as the first or last character.  
These decisions were made based on the latest [NIST Guidelines](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver).

### Admin Features

Channel management (creating, updating, and deleting channels) is restricted to admin users. Standard users will be redirected if they attempt to access these features.

Admin credentials:
- **Username:** `iamtheadmin`
- **Password:** `thisistheadminpassword`

Once logged in as an admin, the channel browser will display "Create Channel" and "Edit Channel" buttons. The edit page also includes a "Delete Channel" button with a confirmation prompt for safety.  
All features exclusive to admins are guarded at the routing level to prevent unauthorised access even through the use of command line prompts and external tools.

### Channel Validation

When creating or updating a channel:
- Channel name must be between 1 and 100 characters.
- Channel name must not already exist (case-insensitive).
- Price must be a valid positive number with at most 2 decimal places.
- Price can be entered with less than 2 decimal places, but will be stored in the standard x.xx format (for example, entering 9.9 will result in a channel priced at £9.90 per month).
- 0 is considered a valid price. This is stored as 0 in the database but shows as 'Free' in the browser. This is purely a visual feature, meaning sorting by price will still show free channels as the cheapest option.

## Hosting

### Render (Web Application)

The Flask application is hosted on [Render](https://render.com) as a web service. Render runs the app using Gunicorn as a production WSGI server. Environment variables (DATABASE_URL, SECRET_KEY) are configured in Render's dashboard to keep sensitive values out of the codebase. Deployments are triggered automatically via a deploy hook URL when the CI/CD pipeline passes.

### Neon (PostgreSQL Database)

The PostgreSQL database is hosted on [Neon](https://neon.tech), a serverless Postgres provider. The connection uses SSL to encrypt data in transit. Although Neon's free tier suspends databases after inactivity, the application includes retry logic with exponential backoff to handle cold starts gracefully.  
Any issue connecting to the database results in a customised error screen displayed to the user for clarity.

## CI/CD Pipeline

The project uses GitHub Actions to automate testing, security scanning, and deployment. The workflow is defined in `.github/workflows/deploy-python-webapp.yml` and runs on every push and pull request to the `master` branch.

### Pipeline Stages

1. **Dependency Installation** — Installs project dependencies and testing tools (flake8, pytest, pytest-mock).
2. **Vulnerability Scanning** — Runs `pip-audit` to check installed packages against known security vulnerabilities.
3. **Linting** — Runs flake8 to check for Python syntax errors, undefined names, and code style issues.
4. **Unit Testing** — Runs the full pytest suite with mocked database connections and environment variables.
5. **Deployment** — If all stages pass, a deployment is triggered to Render via a webhook.

### Pipeline Behaviour

- Pull requests run stages 1–4 only (no deployment), ensuring code quality before merging.
- Pushes to `master` run all stages — deployment only occurs if all checks pass.
- If any stage fails, the pipeline stops and deployment is blocked.
