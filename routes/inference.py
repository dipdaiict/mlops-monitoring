import io
import timm
import torch
from PIL import Image
from fastapi import UploadFile, File, HTTPException, APIRouter

# Routers:
router = APIRouter(prefix="/ml-services", tags=["Health"])

model = None
transforms = None
class_names = None

def load_model():
    global model, transforms, class_names
    model = timm.create_model("resnet18.a1_in1k", pretrained=True)
    model.eval()
    data_config = timm.data.resolve_model_data_config(model)
    transforms = timm.data.create_transform(**data_config, is_training=False)
    imagenet_info = timm.data.ImageNetInfo()
    class_names = imagenet_info.label_descriptions() 
    print(f"Model and transforms loaded successfully with {len(class_names)} classes")

# Load Model:
load_model()


# IMAGE CLASSIFICATION API
@router.post("/v1/get_inference")
async def predict_image(file: UploadFile = File(...)):

    if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        raise HTTPException(status_code=400, detail="Invalid image type")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Preprocess
    input_tensor = transforms(image).unsqueeze(0)

    # Inference
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)[0]

    # Top-5 predictions
    top5_probs, top5_idxs = torch.topk(probs, k=5)

    results = [
        {
            "class_id": int(idx),
            "class_name": class_names[int(idx)].split(",")[0],
            "confidence": round(float(prob) * 100, 2)
        }
        for prob, idx in zip(top5_probs, top5_idxs)
    ]

    return {
        "status": "success",
        "top_5_predictions": results
    }
