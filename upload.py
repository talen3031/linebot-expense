import cloudinary
import cloudinary.uploader
import os
# 請填入你的 Cloudinary 帳號資訊
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


def upload_to_cloudinary(image_path, folder="linebotexpense"):
    """
    上傳本地圖片到 Cloudinary 指定資料夾。
    回傳 (secure_url, public_id)
    """
    result = cloudinary.uploader.upload(
        image_path,
        resource_type="image",
        folder=folder
    )
    return result["secure_url"], result["public_id"]

def delete_from_cloudinary(public_id):
    """
    刪除 Cloudinary 上指定 public_id 的圖片。
    """
    result = cloudinary.uploader.destroy(public_id, resource_type="image")
    return result
