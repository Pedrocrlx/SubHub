FROM nginx:1.27

# Copy the built frontend files to the nginx html directory
COPY ./html /usr/share/nginx/html
COPY ./conf.d/ /etc/nginx/conf.d/

EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]