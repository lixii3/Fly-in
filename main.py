from fly_in import

def main():
    """Start the Fly-in application and report application errors."""
    try:
        Application.run()
    except ApplicationException as e:
        print(e)

if __name__ == "__main__":
    main()
