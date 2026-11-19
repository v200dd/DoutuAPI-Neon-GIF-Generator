FROM php:8.3-apache
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev libjpeg62-turbo-dev libpng-dev libonig-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" gd mbstring \
    && a2enmod headers \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /var/www/html
COPY index.php admin.php config.php .htaccess ./
COPY template/ ./template/
COPY static/ ./static/
COPY neon/fonts/jiying.ttf /usr/share/fonts/doutu.ttf
COPY docker/php-apache.conf /etc/apache2/conf-enabled/doutu.conf
COPY docker/php-production.ini /usr/local/etc/php/conf.d/doutu.ini
COPY docker/php-entrypoint.sh /usr/local/bin/doutu-entrypoint
RUN chmod +x /usr/local/bin/doutu-entrypoint && mkdir -p /var/lib/doutu
ENTRYPOINT ["doutu-entrypoint"]
CMD ["apache2-foreground"]
