# Food-Rekognition
Recognizing food in images using AWS and Amazon Rekognition

## Overview
Food Rekognition is a cloud native, serverless architecture built on AWS that takes an image as input by exposing public HTTP API, analyzes image for food items via lambda using Amazon Rekognition and Amazon S3, and returns an analyzed image with each food identified. With a personal interest in nutrition, the goal of this project was to integrate real world AWS services but also test its capabilities in identifying food from every day images, inspired by photo AI nutrition tracking apps.

## AWS Architecture
<img width="596" height="286" alt="Screenshot 2026-01-13 at 7 37 40 AM" src="https://github.com/user-attachments/assets/9d644163-b9a3-4c07-a26e-92554a860ab7" />


1.	An image is sent via public HTTP API as a Base64-encoded payload to API Gateway. 
2.	Then, API Gateway invokes the lambda function which uploads the image (after safety checks) to Amazon S3 bucket. 
3.	Lambda function (```food_recognition_handler```) invokes Amazon Rekognition which takes key of image from S3 bucket. Rekognition analyzes image.
4.	Lambda returns detected labels and locations of those labels (boxes)
5.	A local python file takes these labels and uses ```matplotlib``` to visualize results.

## Services Used
-	API Gateway
    *	HTTP API was used since this was a public facing API and only needed to invoke Lambda. HTTP API was the perfect lightweight choice for this task compared to a more costly and complicated REST API.
-	Lambda
    *	The core computation layer of the architecture
    *	Triggered by event from by API Gateway
    *	Manages calls to and from other AWS services
    *	(This felt more familiar to python scripts I have been used to writing.)
-	Amazon S3
    *	Temporarily stores image for Rekognition to access data securely
    *	Objects are deleted after Rekognition is done obtaining labels.
-	Amazon Rekognition
    *	(Honestly a really cool tool. It does feel like a black box, but surprisingly very powerful.)
-	IAM
    *	IAM execution roles allowed Lambda to access other services such as S3 and Rekognition
    *	Used least privileged permissions (see costs and security)

## Examples/Results
Input/output
Lambda will return a JSON that looks like this:
```
{
  "best_guess": "Pizza",
  "labels": [
    {
      "name": "Pizza",
      "confidence": 99.6,
      "boxes": [
        {
          "left": 0.08,
          "top": 0.10,
          "width": 0.79,
          "height": 0.78
        }
      ]
    }
  ]
}
```
When a simple picture of a pizza is inputted, we get this result:

<img width="493" height="280" alt="Screenshot 2026-01-13 at 7 37 59 AM" src="https://github.com/user-attachments/assets/8e74fd3b-bfc4-4512-b82d-307c9d2ae6dc" />

I found that rekognition works well with simple images such as:

<img width="397" height="218" alt="Screenshot 2026-01-13 at 7 40 22 AM" src="https://github.com/user-attachments/assets/b78bbaa5-3c94-4b82-8e88-f693b2f4a610" />

 
But it seems to work poorly with more complicated images

<img width="251" height="163" alt="Screenshot 2026-01-13 at 7 40 34 AM" src="https://github.com/user-attachments/assets/d3042dc4-c68a-4495-815f-5dafe05f5b15" />

 
And also have a high affinity to guess pork on lower quality images:
 
<img width="284" height="168" alt="Screenshot 2026-01-13 at 7 40 54 AM" src="https://github.com/user-attachments/assets/0348e77b-748a-441f-ab29-ba3271cf38e5" />
<img width="281" height="198" alt="Screenshot 2026-01-13 at 7 41 04 AM" src="https://github.com/user-attachments/assets/5bf82f3c-2c0a-4908-aa33-a2dc83d952f7" />



## Security and Cost
-	Food Rekognition uses least privilege IAM, which means Lambda’s execution role is restricted to only required actions in S3 and Rekognition.
    *	For example, the lambda function has access to ```rekognition:DetectLabels``` but does not have blanket access to rekognition.
-	Access to S3 bucket is only allowed by lambda via IAM
-	No API keys or credentials or the API URL is available in this repository.
-	By creating an API key and usage plans, we can limit rate and burst.
-	Image size is limited in Lambda.
-	Images are only temporarily stored in S3 and deleted once Rekognition is done.
-	This project was built to be in free tier since all components are relatively inexpensive and can be run in the free plan with AWS.

## Future Considerations
-	To create a more reproducible and deployable architecture, this project could be converted to infrastructure as code (IaC) using AWS SAM or Terraform. 
-	While machine learning was not the primary focus, it would be interesting to see if we could obtain a better model for food classification, and Amazon Rekognition’s Custom Labels seems like the next step in exploring this idea.
