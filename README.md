# Flask Cloudflare DNS Crud App

This is a simple CRUD app for managing DNS records through cloudflare. 

## Who is this for?

The cloudflare UI can be slow if it starts to hog memory. Deploy this app in your homelab to add a faster, simpler UI.

## Features
- Add a DNS record
- Modify a DNS record
- Delete a DNS record
- Search DNS records

## Screenshot
![Basic UI for DNS records](https://github.com/user-attachments/assets/06d07b4d-9497-45be-b8bd-35a6cf525ad1)


## Instructions to Create a Cloudflare API Token

1. **Log in to Cloudflare**:
   - Visit [Cloudflare's Dashboard](https://dash.cloudflare.com/login) and log in with your credentials.

2. **Navigate to API Tokens**:
   - Click on your profile icon in the upper right corner.
   - Select **My Profile** from the dropdown menu.
   - Go to the **API Tokens** tab.

3. **Create a New API Token**:
   - Click on **Create Token**.

4. **Configure the API Token**:
   - **Template**: Select **Create Custom Token**.
   
   - **Token Name**: Give your token a descriptive name, e.g., `DNS CRUD App Token`.
   
   - **Permissions**:
     - **Zone**:
       - **Zone**: Read
       - **DNS**: Edit
   - **Zone Resources**: 
     - **Include**: All zones or specify your domain if you want to restrict it to a particular domain.

5. **Create and Save the Token**:
   - Click **Continue to Summary**.
   - Review the token settings.
   - Click **Create Token**.
   - **Copy the token** and store it securely, as this will be the only time you can view it.

6. **Update Your .env File**:
   - Open your `.env` file in your project directory.
   - Add or update the following line with your new token:
     ```
     CLOUDFLARE_API_TOKEN=your_token_here
     ```

### Example `.env` File
```env
APP_PASSWORD=your_app_password
CLOUDFLARE_API_TOKEN=your_newly_created_token
DOMAIN=your_domain_here
```

### Summary of Token Permissions
- **Zone**: Read
- **DNS**: Edit

These permissions will allow your application to read and modify DNS records for the specified zone(s). 

### Final Steps
- **Restart your Flask application** to ensure it picks up the new token from the `.env` file:
  ```sh
  flask run
  ```

Following these steps will enable your Flask application to interact with the Cloudflare API to manage DNS records.

