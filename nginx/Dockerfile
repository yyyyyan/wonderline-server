FROM nginx:1.19.1
COPY nginx.conf /etc/nginx/nginx.conf

RUN rm /etc/nginx/conf.d/default.conf
COPY project.conf /etc/nginx/conf.d/