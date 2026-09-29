#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         📊 МОНИТОРИНГ НЕЙВА МИЛК (Real-time)                  ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ Время          │ UUID     │ Датчик        │ Значение │ Статус ║"
echo "╚════════════════════════════════════════════════════════════════╝"

sudo docker logs -f nevamilk-analytics-1 2>&1 | \
while read -r line; do
    # Извлекаем время
    timestamp=$(echo "$line" | grep -oP 'time=\K[0-9T:\.-]+Z' | head -1)
    timestamp=$(echo "$timestamp" | sed 's/T/ /' | cut -c12-19)
    
    # Извлекаем UUID
    uuid=$(echo "$line" | grep -oP '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
    uuid_short="${uuid:0:8}"
    
    # Проверяем на ошибку
    if echo "$line" | grep -q "ERROR"; then
        status="${RED}❌ ОШИБКА${NC}"
        error_type=$(echo "$line" | grep -oP 'msg="\K[^"]+' | head -1)
        sensor="${YELLOW}UNKNOWN${NC}"
        value="---"
    else
        status="${GREEN}✅ ОК${NC}"
        
        # Извлекаем base64 payload
        b64=$(echo "$line" | grep -oP 'payload="\K[^"]+' | grep -oP '\.[A-Za-z0-9+/=]+$' | tail -c +2)
        
        if [ -n "$b64" ]; then
            # Декодируем JSON
            decoded=$(echo "$b64" | base64 -d 2>/dev/null)
            
            # Парсим JSON
            category=$(echo "$decoded" | grep -oP '"category":"\K[^"]+')
            data=$(echo "$decoded" | grep -oP '"data":\K[0-9\.]+')
            
            # Красивые названия датчиков
            case "$category" in
                "temperature") sensor="${BLUE}🌡️  Температура${NC}" ;;
                "humidity")    sensor="${BLUE}💧 Влажность${NC}" ;;
                "pH Sensor")   sensor="${BLUE}🧪 pH${NC}" ;;
                "load Cell")   sensor="${BLUE}📊 Давление${NC}" ;;
                "vibration")   sensor="${BLUE}📳 Вибрация${NC}" ;;
                *)             sensor="${YELLOW}❓ $category${NC}" ;;
            esac
            
            value="$data"
        else
            # Warning сообщение
            warn_msg=$(echo "$line" | grep -oP 'payload="\K[^"]+' | grep -v "\.")
            if [ -n "$warn_msg" ]; then
                sensor="${RED}⚠️  WARNING${NC}"
                value="$warn_msg"
            fi
        fi
    fi
    
    # Вывод строки
    printf "${NC}%s │ %s │ %-13b │ %8s │ %b${NC}\n" \
        "$timestamp" "$uuid_short" "$sensor" "$value" "$status"
    
done
