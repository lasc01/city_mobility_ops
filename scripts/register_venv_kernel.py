from ipykernel.kernelspec import install

def main():
    install(
        user=True,
        kernel_name="city_mobility_venv",
        display_name="Python (city_mobility_ops .venv)"
    )
    print("kernel installed: Python (city_mobility_ops .venv)")

if __name__ == "__main__":
    main()