this is a ai agent that can use external api keys from the gemini and groc
to run the application first install docker for linux 
for windows install docker applicaton for windows to makes sure docker engine is running 
give proper permissions to the docker on your system be it in linux or windows
make a image of the agent on you local computer usning the command "docker swarm up -d --build"
check image name using the command "docker images"
after build is done simply run the command "docker exec -it <image_name> ai"
do the startup setup this is not onetime and can be changed later
enter the api keys and dont worry if it is not visible on your screen just paste it
to exit the session just type exit
to stop the container from using your resources just type the command "docker compose down"
