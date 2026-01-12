import argparse
import base64
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg


api_url = None

def visualize(image_path: str, api_url: str):
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = requests.post(
        api_url,
        json={"image_b64": image_b64},
        timeout=60
    )
    response.raise_for_status()
    data = response.json()

    foods = data.get("foods", [])
    best_guess = data.get("best_guess")

    img = mpimg.imread(image_path)
    height, width = img.shape[:2]

    fig, ax = plt.subplots(1)
    ax.imshow(img)
    ax.axis("off")

    box_count = 0

    for food in foods:
        name = food.get("name", "Unknown")
        confidence = food.get("confidence")

        for box in food.get("boxes", []):
            x = box["left"] * width
            y = box["top"] * height
            w = box["width"] * width
            h = box["height"] * height

            rect = patches.Rectangle(
                (x, y),
                w,
                h,
                linewidth=2,
                edgecolor="red",
                facecolor="none"
            )
            ax.add_patch(rect)

            label_conf = box.get("confidence", confidence)
            label = (
                f"{name}"
                if label_conf is None
                else f"{name} ({label_conf:.1f}%)"
            )

            ax.text(
                x,
                max(0, y - 6),
                label,
                color="red",
                fontsize=10,
                bbox=dict(
                    facecolor="white",
                    alpha=0.7,
                    edgecolor="none"
                )
            )
            box_count += 1
    if box_count == 0:
        plt.title("No recognized food in this image")
    
    plt.show()



def main():
    parser = argparse.ArgumentParser(description="Food Rekognition")
    parser.add_argument("image", help="Path to image file")
    args = parser.parse_args()
    
    if api_url == None:
        print("Please include a vald api url")
    else:
        visualize(args.image, api_url)


if __name__ == "__main__":
    main()

