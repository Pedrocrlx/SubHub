FROM nginx:1.27

# Copy the built frontend files to the nginx html directory
COPY . /usr/share/nginx/html

# Start nginx
CMD ["nginx", "-g", "daemon off;"]