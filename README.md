Desplegar mi codigo de Flask sobre Gunicorn y Nginx
=============
Utilice ubuntu para hacer estas configuraciones ya que ví que no estaban disponible para Windows, abajo le dejo las configuraciones que hice para el Gunicorn y el Nginx.

primero que todo vemos que nuestro programa no presente ningu fallo (receta_flask.py) y el archivo .html esten en una dirección donde el programa puede localizarlo para que no nos presente un error de cualquier tipo. 

si todo esta bien y el programa ejecuta, les debera aparecer algo similar a lo siguiente:




```python
(myenv) root@Said-Pe:~/projects/receta_Flaskdb# python receta_flask.py
Serving Flask app 'receta_flask'
 Debug mode: on`
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 Running on all addresses (0.0.0.0)
 Running on http://127.0.0.1:5000
 Running on http://172.23.241.122:5000
 Press CTRL+C to quit
Restarting with stat
 Debugger is active!
 Debugger PIN: 142-156-360
```

una vez que sepamos que nuestro programa no presente fallos, utilizamos el comando: **gunicorn --bind 0.0.0.0:5000 wsgi:app** para iniciar el servidor y nos deberia aparecer lo siguiente: 

```python
	(myenv) root@Said-Pe:~/projects/receta_Flaskdb# gunicorn --bind 0.0.0.0:5000 wsgi:app
	[2024-04-21 14:53:01 -0500] [12919] [INFO] Starting gunicorn 22.0.0
	2024-04-21 14:53:01 -0500] [12919] [INFO] Listening at: http://0.0.0.0:5000 (12919)  [2024-04-21 14:53:01 -0500] [12919] [INFO] Using worker: sync
	[2024-04-21 14:53:01 -0500] [12921] [INFO] Booting worker with pid: 12921
```

Ya que vemos que nos responde a continuación, crearemos el archivo de unidad de servicio systemd. Crear un archivo de unidad systemd permitirá que el sistema init de 
Ubuntu inicie automáticamente Gunicorn y haga funcionar la aplicación de Flask cuando el servidor se cargue.

Creamos un archivo de unidad terminado en .service dentro del directorio `/etc/systemd/system ` para empezar (Le muestro la dirrección en mi directorio y el codigo introducido en mi rflask.service):

    #Mi directorio
	root@Said-Pe:/etc/nginx/sites-available# cat /etc/systemd/system/rflask.service

## archivo rflask.service
    [Unit]
    Description=Flask Application
    After=network.target
    
    [Service]
    User=root
    Group=www-data
    WorkingDirectory=/root/projects/receta_Flaskdb
    Environment="PATH=/root/projects/receta_Flaskdb/myenv/bin"
    ExecStart=/root/projects/receta_Flaskdb/myenv/bin/gunicorn --workers 3 --bind unix:receta_flask.sock -m 007 wsgi:app
    
    [Install]
    WantedBy=multi-user.target
    root@Said-Pe:/etc/nginx/sites-available#


Con eso, nuestro archivo de servicio de systemd quedará completo. 

Ya podemos iniciar el servicio Gunicorn que creamos y activarlo para que se cargue en el inicio:

    sudo systemctl start rflask
    sudo systemctl enable rflask
Comprobemos el estado con:  `sudo systemctl status rflask.service`
    
    root@Said-Pe:/etc/nginx/sites-available# sudo systemctl status rflask.service
    ● rflask.service - Flask Application
         Loaded: loaded (/etc/systemd/system/rflask.service; enabled; vendor preset: enabled)
         Active: active (running) since Sun 2024-04-21 14:00:57 EST; 1h 45min ago
       Main PID: 274 (gunicorn)
          Tasks: 4 (limit: 4379)
         Memory: 75.4M
         CGroup: /system.slice/rflask.service
                 ├─274 /root/projects/receta_Flaskdb/myenv/bin/python3 /root/projects/receta_Flaskdb/myenv/bin/gunicorn --workers 3 --bind unix:receta_flask.sock -m 007 wsgi>
                 ├─358 /root/projects/receta_Flaskdb/myenv/bin/python3 /root/projects/receta_Flaskdb/myenv/bin/gunicorn --workers 3 --bind unix:receta_flask.sock -m 007 wsgi>
                 ├─388 /root/projects/receta_Flaskdb/myenv/bin/python3 /root/projects/receta_Flaskdb/myenv/bin/gunicorn --workers 3 --bind unix:receta_flask.sock -m 007 wsgi>
                 └─390 /root/projects/receta_Flaskdb/myenv/bin/python3 /root/projects/receta_Flaskdb/myenv/bin/gunicorn --workers 3 --bind unix:receta_flask.sock -m 007 wsgi>
    
    Apr 21 14:00:57 Said-Pe systemd[1]: Started Flask Application.
    Apr 21 14:00:58 Said-Pe gunicorn[274]: [2024-04-21 14:00:58 -0500] [274] [INFO] Starting gunicorn 22.0.0
    Apr 21 14:00:58 Said-Pe gunicorn[274]: [2024-04-21 14:00:58 -0500] [274] [INFO] Listening at: unix:receta_flask.sock (274)
    Apr 21 14:00:58 Said-Pe gunicorn[274]: [2024-04-21 14:00:58 -0500] [274] [INFO] Using worker: sync
    Apr 21 14:00:58 Said-Pe gunicorn[358]: [2024-04-21 14:00:58 -0500] [358] [INFO] Booting worker with pid: 358
    Apr 21 14:00:58 Said-Pe gunicorn[388]: [2024-04-21 14:00:58 -0500] [388] [INFO] Booting worker with pid: 388
    Apr 21 14:00:58 Said-Pe gunicorn[390]: [2024-04-21 14:00:58 -0500] [390] [INFO] Booting worker with pid: 390

Si nos aparece esto vamos por buen camino, ahora vamos a configurar Nginx para solicitudes de proxy

## Configurar Nginx para solicitudes de proxy
Configuramos Nginx para que actúe como un servidor proxy para dirigir las solicitudes web al servidor de aplicación Gunicorn. 

1. Crear un nuevo archivo de configuración de bloque de servidor en el directorio` sites-available de Nginx.`
2. Nombrar el archivo de configuración como rflask.
3. Este archivo de configuración contendrá las directivas necesarias para configurar Nginx como un proxy para las solicitudes web dirigidas al servidor de aplicación Gunicorn.

creamos el archivo con: 
`sudo nano /etc/nginx/sites-available/rflask`
A continuación, agregaremos un bloque de ubicación que coincida con cada solicitud. Dentro de este bloque, incluiremos el archivo proxy_params que especifica algunos parámetros de proxy generales que deben configurarse. Luego, pasaremos las solicitudes al socket que definimos usando la directiva proxy_pass:

## Configurar el archivo rflask
    server {
        listen 80;
        server_name www.recetasflask.com;
    
        location / {
            include proxy_params;
            proxy_pass http://unix:/home/sammy/myproject/receta_flask.sock;
        }
    }

Guarde y cierre el archivo al finalizar.

Para habilitar la configuración del bloque de servidor de Nginx que acaba de crear, vincule el archivo al directorio` sites-enabled`:

    sudo ln -s /etc/nginx/sites-available/rflask /etc/nginx/sites-enabled

Si no se indican problemas, reinicie el proceso de Nginx para que lea la nueva configuración:

    sudo systemctl restart nginx

con esto ya tenemos todo configurado.
####ESO ES TODA MI CONFIGURACIÓN DE GUNICORN Y NGINX, GRACIAS POR LEER.
