FROM php:7.4-apache
RUN docker-php-ext-install mysqli pdo pdo_mysql && docker-php-ext-enable mysqli pdo pdo_mysql
RUN a2enmod rewrite
COPY ./src /var/www/html/
RUN chown -R www-data:www-data /var/www/html/ \
    && chmod -R 755 /var/www/html/
EXPOSE 80
