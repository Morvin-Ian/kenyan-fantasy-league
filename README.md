# 🇰🇪 Kenyan Fantasy League (KFL)

Welcome to the **Kenyan Fantasy League (KFL)** – the premier platform for fantasy sports enthusiasts in Kenya!  
Whether you're passionate about football or other popular sports, **KFL** lets you create and manage your own fantasy teams.

 Test your sports knowledge,  compete with friends and family, and climb the leaderboards as you enjoy the thrill of fantasy sports like never before!


## Running the Project Locally

To run KFL on your local machine using Docker:

```bash
# Step 1: Copy the example environment file
cp .env.example .env

# Step 2: Build the containers
docker compose build

# Step 3 (Optional): Stop and remove containers/volumes
docker compose down -v

# Step 4: Start the application
docker compose up
                                             