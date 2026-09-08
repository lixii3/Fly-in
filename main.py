from fly_in import

def main():
    try:
        Application.run()
    except ApplicationException as e:
        print(e)

if __name__ == "__main__":
    main()
