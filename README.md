# Force Graph Project 

## Description

MDL-570 is a life insurance regulation that is dependent on other regulations, which in turn reference additional regulations, creating a complex web of dependencies that can be visualized as a clickable dependency graph or force-graph, showing all dependencies up to 5 levels.

## How to Run

### Backend

1. Navigate to the `backend` directory:
    ```sh
    cd backend
    ```
2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Run the backend server:
    ```sh
    python main.py
    ```

### Frontend

1. Navigate to the [frontend](http://_vscodecontentref_/1) directory:
    ```sh
    cd frontend
    ```
2. Install the required dependencies:
    ```sh
    npm install
    ```
3. Run the frontend development server:
    ```sh
    npm start
    ```

    The frontend will be available at [http://localhost:3000](http://localhost:3000).

## Deployed URL

1. To deploy the development server:
    ```sh
    npm run deploy
    ```
2. The project is deployed at: [https://kiran-kumarr.github.io/forced-graph/](https://kiran-kumarr.github.io/forced-graph/)
