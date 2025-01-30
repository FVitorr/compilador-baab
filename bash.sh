#!/bin/bash

# Verifique se o argumento foi passado corretamente
if [ "$#" -ne 2 ] || [ "$2" != "-c" ]; then
  echo "Uso correto: b-a-ba <parametro> -c <arquivo>"
  exit 1
fi

# Chame o script Python passando o arquivo
python3 main.py "$2"
