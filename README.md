# TALK TO TARTAN PROJECT

## System Architecture

![Screenshot 2024-12-12 174414](https://github.com/user-attachments/assets/58429c65-e4a0-4a06-b620-ebc58d9e0210)

## Clone the repo
```
git clone https://github.com/teddyk251/Talk-to-Tartan.git
```
## Create and activate  virtual environment.
Ensure you have Conda installed in your system
```
conda create --name myenv python=3.10
```
```
conda activate myenv
```
## Getting Started
1. **Create a virtual environment and install the required packages:**

```
cd chainlit
pip install -r requirements.txt
```
2. **Create a `.env` file and add your `OPENAI_API_KEY`:**

    ```sh
    echo "OPENAI_API_KEY=your_openai_api_key" > .env
    ```

### Running the Program
Run each of the following on a separate terminal session.
1. **Run the backend application**
```
cd backend
python api.py
```
2. **Start Chainlit Application**
```
cd chainlit
chainlit run main2.py -w
```
3. **Start the Front-end Application**
```
cd frontend_app
python app.py
```


