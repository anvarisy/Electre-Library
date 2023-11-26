import io
import os
from fastapi import APIRouter, Form, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from fastapi import File, UploadFile

from electre import Electre

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def view_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "name": " & Welcome Back To Electre !"})

@router.get("/upload", response_class=HTMLResponse)
async def view_upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

UPLOAD_DIR = "upload"
@router.post("/post-upload")
async def upload_data(file: UploadFile = File(...)):
        try:
            if file.content_type != "text/csv":
                raise HTTPException(status_code=400, detail="File type not supported")
            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)

            # Menyimpan file ke direktori yang ditentukan
            with open(os.path.join(UPLOAD_DIR, file.filename), "wb") as buffer:
                contents = await file.read()  # baca file
                buffer.write(contents)

            files = []
            if os.path.exists(UPLOAD_DIR):
                files = os.listdir(UPLOAD_DIR)
            
            return {
                "error": "",
                "status": True,
                "data": files
            }
    
        except HTTPException as e:
            return {
                "error": e.detail,
                "status": False,
                "data": []
            }

@router.get("/calculate", response_class=HTMLResponse)
async def view_home(request: Request):
    files = None
    if os.path.exists(UPLOAD_DIR):
        files = os.listdir(UPLOAD_DIR)
    return templates.TemplateResponse("calculate.html", {"request": request, "files":files, "error":""})

@router.post("/post-calculate", response_class=HTMLResponse)
async def train_result(
    request: Request,
    selectedFile: str = Form(...),
    weights: str = Form(...),
):
    filename = f'./upload/{selectedFile}'
    df = pd.read_csv(filename)
    # selected_columns = ['K1', 'K2', 'K3', 'K4', 'K5']
    kolom_tidak_berguna = 'Nama Salesman'

    # Menghapus kolom yang tidak berguna
    df_filtered = df.drop(columns=[kolom_tidak_berguna])
    # df_filtered = df[selected_columns]

    # Mengonversi DataFrame menjadi matriks
    data_matrix = df_filtered.values.tolist()

    array_output = [int(item.strip()) for item in weights.split(',')]
    weight_size = len(array_output)
    colomn_size = len(data_matrix[0])
    if(weight_size != colomn_size):
        files = None
        if os.path.exists(UPLOAD_DIR):
            files = os.listdir(UPLOAD_DIR)
        return templates.TemplateResponse("calculate.html", {"request": request, "files":files, "error":"Jumlah kriteria & bobot tidak sama !"})
    e = Electre()
    try:
        res = e.start(data_matrix, array_output)
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request})
    df['Hasil Proses'] = res

    # Mengurutkan DataFrame berdasarkan kolom baru
    df_sorted = df.sort_values(by='Hasil Proses', ascending=False)

    # Mengubah DataFrame menjadi string CSV
    csv_string = df_sorted.to_csv(index=False)
    output_filename = 'hasil_electre.csv'
    df_sorted.to_csv(f'./static/result/{output_filename}', index=False)
    return templates.TemplateResponse(
        "results.html", {"request": request, "csv_data": csv_string, "path":f'/static/result/{output_filename}', "router": router}
    )

@router.get("/download-csv")
async def download_csv(
     request: Request,
     output_filename: str = Query(..., alias="output_filename")
):
    file_path = f'.{output_filename}'
    name = "result"
    # Membaca file CSV sebagai bytes
    with open(file_path, "rb") as file:
        csv_bytes = file.read()

    # Menanggapi unduhan dengan menggunakan StreamingResponse
    return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{output_filename}"'})


