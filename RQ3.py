import create_maps
import prism_model_generator


def main():
    create_maps.create_3_maps()
    for i in range(0, 3):
        prism_model_generator.generate_model(i)


if __name__ == '__main__':
    main()
