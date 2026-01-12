import json
import base64
import uuid
import boto3

s3 = boto3.client("s3")
rek = boto3.client("rekognition")
BUCKET_NAME = "food-recognition-images-0001"

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    body = event.get("body")
    if body is None:
        return response(400, {"error": "Missing body"})


    try:
        payload = json.loads(body)
        image_bytes = base64.b64decode(payload["image_b64"], validate=True)
    except Exception:
        return response(400, {"error": "Bad request"})

    if len(image_bytes) > 10 * 1024 * 1024:
        return response(413, {"error": "Image too large (max 10MB)"})

    # Upload to S3
    image_id = str(uuid.uuid4())
    s3_key = f"uploads/{image_id}.jpg"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=image_bytes,
        ContentType="image/jpeg"
    )

    # Rekognition step
    try:
        rek_resp = rek.detect_labels(
            Image={"S3Object": {"Bucket": BUCKET_NAME, "Name": s3_key}},
            MaxLabels=10,
            MinConfidence=60.0
        )
        
    except Exception as e:
        return response(500, {
            "error": "Rekognition DetectLabels failed",
            "details": str(e)
        })
    

    labels = rek_resp.get("Labels", []) or []

    s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)

    GENERIC = {"Food", "Meal", "Dish", "Cuisine", "Food Presentation"}

    foods = []
    for l in labels:
        name = l.get("Name")
        conf = float(l.get("Confidence", 0.0))
        instances = l.get("Instances") or []

        if name in GENERIC:
            continue

        boxes = []
        for inst in instances:
            bb = inst.get("BoundingBox")
            if not bb:
                continue
            boxes.append({
                "left": bb.get("Left"),
                "top": bb.get("Top"),
                "width": bb.get("Width"),
                "height": bb.get("Height"),
                "confidence": round(float(inst.get("Confidence", conf)), 2)
            })

        foods.append({
            "name": name,
            "confidence": round(conf, 2),
            "boxes": boxes
        })

    best_guess = foods[0]["name"] if foods else None

    return response(200, {
        "best_guess": best_guess,
        "foods": foods
    })
