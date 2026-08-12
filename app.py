import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from google.cloud import bigquery

# ==========================================
# 1. הגדרות עמוד
# ==========================================
st.set_page_config(
    page_title="מערכת אופטימיזציית אריזה 3D - KSP", page_icon="📦", layout="wide"
)

st.title("📦 מערכת אופטימיזציית אריזה ותצוגת 3D")
st.markdown(
    "מערכת חיבור בלייב ל-BigQuery: בחירת מק\"ט מהמלאי, התאמה ל-4 הקרטונים,"
    " חישוב ניצול נפח והדמיה תלת-ממדית."
)

# ==========================================
# 2. הגדרת 4 הקרטונים מ-BigQuery
# ==========================================
CARTONS = {
    "קבוצה 1 (סטנדרטית / בינונית)": {
        "L": 880.0,
        "W": 481.0,
        "H": 295.0,
        "color": "#1f77b4",
    },
    "קבוצה 2 (רחבה וארוכה)": {
        "L": 1910.0,
        "W": 880.0,
        "H": 390.0,
        "color": "#ff7f0e",
    },
    "קבוצה 3 (נפחית / גבוהה)": {
        "L": 1020.0,
        "W": 830.0,
        "H": 670.0,
        "color": "#9467bd",
    },
    "קבוצה 4 (ארוכה וצרה)": {
        "L": 2030.0,
        "W": 460.0,
        "H": 290.0,
        "color": "#17becf",
    },
}


# ==========================================
# 3. טעינת כל המק"טים מ-BigQuery (עם זיכרון מטמון למהירות)
# ==========================================
@st.cache_data(ttl=600)  # רענון נתונים אוטומטי כל 10 דקות
def load_data_from_bigquery():
  try:
    client = bigquery.Client()
    query = """
            SELECT 
                CAST(SKU AS STRING) AS SKU,
                Item_Name,
                CAST(Box_L AS FLOAT64) AS Box_L,
                CAST(Box_W AS FLOAT64) AS Box_W,
                CAST(Box_H AS FLOAT64) AS Box_H
            FROM `responsive-sun-386807.real_single_items_warehouse_package.warehouse_package`
            WHERE Box_L IS NOT NULL AND Box_W IS NOT NULL AND Box_H IS NOT NULL
        """
    df = client.query(query).to_dataframe()
    return df
  except Exception as e:
    # גיבוי במקרה של הרצה מקומית ללא מפתח BigQuery
    st.sidebar.warning(
        "טוען נתוני גיבוי מקומיים (חבר מפתח GCP לטעינה מלאה מ-BigQuery)"
    )
    return pd.DataFrame([
        {
            "SKU": "100019",
            "Item_Name": "מסך מחשב קעור 27 אינץ'",
            "Box_L": 620.0,
            "Box_W": 400.0,
            "Box_H": 180.0,
        },
        {
            "SKU": "200045",
            "Item_Name": "מקלדת מכנית גיימינג",
            "Box_L": 450.0,
            "Box_W": 150.0,
            "Box_H": 40.0,
        },
        {
            "SKU": "300088",
            "Item_Name": "מארז מחשב Tower",
            "Box_L": 520.0,
            "Box_W": 280.0,
            "Box_H": 510.0,
        },
        {
            "SKU": "400012",
            "Item_Name": "זרוע כפולה לכל מסך",
            "Box_L": 950.0,
            "Box_W": 220.0,
            "Box_H": 130.0,
        },
    ])


df_items = load_data_from_bigquery()

# ==========================================
# 4. סיידבאר: לבחירה מתוך כל המק"טים
# ==========================================
st.sidebar.header("🔎 איתור מוצר מהמלאי")
search_mode = st.sidebar.radio(
    "שיטת בחירה:", ["בחירה מרשימת המק\"טים המלאה", "הזנת מידות ידנית"]
)

item_L, item_W, item_H = 0.0, 0.0, 0.0
item_label = ""

if search_mode == 'בחירה מרשימת המק"טים המלאה':
  # יצירת רשימה נפתחת (Dropdown) עם כל המק"טים ושמותיהם
  df_items["display_name"] = (
      df_items["SKU"] + " - " + df_items["Item_Name"].fillna("")
  )
  selected_display = st.sidebar.selectbox(
      f"בחר מק\"ט מתוך {len(df_items)} מוצרים במאגר:",
      options=df_items["display_name"].tolist(),
  )

  selected_row = df_items[df_items["display_name"] == selected_display].iloc[0]
  item_L = float(selected_row["Box_L"])
  item_W = float(selected_row["Box_W"])
  item_H = float(selected_row["Box_H"])
  item_label = f"{selected_row['Item_Name']} (מק\"ט: {selected_row['SKU']})"
else:
  st.sidebar.subheader("מידות המוצר (מ\"מ)")
  item_L = st.sidebar.number_input("אורך L", min_value=10.0, value=500.0)
  item_W = st.sidebar.number_input("רוחב W", min_value=10.0, value=300.0)
  item_H = st.sidebar.number_input("גובה H", min_value=10.0, value=150.0)
  item_label = "מוצר מוזן ידנית"

# ==========================================
# 5. לוגיקת התאמת קרטון וחישוב ניצול נפח
# ==========================================
item_volume = item_L * item_W * item_H
valid_options = []

for group_name, dims in CARTONS.items():
  if item_L <= dims["L"] and item_W <= dims["W"] and item_H <= dims["H"]:
    carton_vol = dims["L"] * dims["W"] * dims["H"]
    utilization = (item_volume / carton_vol) * 100
    waste = carton_vol - item_volume
    valid_options.append({
        "group_name": group_name,
        "dims": dims,
        "utilization": utilization,
        "waste": waste,
    })

# ==========================================
# 6. הצגת מדדים (KPIs)
# ==========================================
if not valid_options:
  st.error(
      f"🚨 המוצר **{item_label}** ({item_L}x{item_W}x{item_H} מ\"מ) חורג ממידות"
      " כל 4 הקרטונים במחסן!"
  )
else:
  best = min(valid_options, key=lambda x: x["waste"])

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("שם המוצר שנבחר", item_label)
  col2.metric("קבוצת קרטון מומלצת", best["group_name"])
  col3.metric(
      "מידות קרטון (L x W x H)",
      f"{int(best['dims']['L'])} x {int(best['dims']['W'])} x {int(best['dims']['H'])} מ\"מ",
  )
  col4.metric("ניצול נפח", f"{best['utilization']:.1f}%")

  st.divider()

  # ==========================================
  # 7. הדמיית תלת-ממד (3D)
  # ==========================================
  def get_box_lines(x0, y0, z0, dx, dy, dz, name, color):
    x = [
        x0,
        x0 + dx,
        x0 + dx,
        x0,
        x0,
        x0,
        x0 + dx,
        x0 + dx,
        x0,
        x0,
        x0 + dx,
        x0 + dx,
        x0 + dx,
        x0 + dx,
        x0,
        x0,
    ]
    y = [
        y0,
        y0,
        y0 + dy,
        y0 + dy,
        y0,
        y0,
        y0,
        y0 + dy,
        y0 + dy,
        y0 + dy,
        y0 + dy,
        y0,
        y0,
        y0 + dy,
        y0 + dy,
        y0,
    ]
    z = [
        z0,
        z0,
        z0,
        z0,
        z0,
        z0 + dz,
        z0 + dz,
        z0 + dz,
        z0 + dz,
        z0,
        z0,
        z0,
        z0 + dz,
        z0 + dz,
        z0 + dz,
        z0 + dz,
    ]
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=name,
        line=dict(color=color, width=3),
    )

  def get_box_mesh(x0, y0, z0, dx, dy, dz, name, color, opacity=0.3):
    x = [x0, x0 + dx, x0 + dx, x0, x0, x0 + dx, x0 + dx, x0]
    y = [y0, y0, y0 + dy, y0 + dy, y0, y0, y0 + dy, y0 + dy]
    z = [z0, z0, z0, z0, z0 + dz, z0 + dz, z0 + dz, z0 + dz]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    return go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        name=name,
        color=color,
        opacity=opacity,
        showscale=False,
    )

  fig = go.Figure()
  fig.add_trace(
      get_box_mesh(
          0,
          0,
          0,
          best["dims"]["L"],
          best["dims"]["W"],
          best["dims"]["H"],
          best["group_name"],
          best["dims"]["color"],
          opacity=0.15,
      )
  )
  fig.add_trace(
      get_box_lines(
          0,
          0,
          0,
          best["dims"]["L"],
          best["dims"]["W"],
          best["dims"]["H"],
          "מסגרת קרטון",
          best["dims"]["color"],
      )
  )
  fig.add_trace(
      get_box_mesh(
          0, 0, 0, item_L, item_W, item_H, "המוצר", "green", opacity=0.75
      )
  )
  fig.add_trace(
      get_box_lines(0, 0, 0, item_L, item_W, item_H, "מסגרת מוצר", "darkgreen")
  )

  fig.update_layout(
      title=dict(
          text=f"<b>הדמיית אריזה בתלת-ממד עבור {best['group_name']}</b>",
          x=0.5,
      ),
      scene=dict(
          xaxis_title='אורך (מ"מ)',
          yaxis_title='רוחב (מ"מ)',
          zaxis_title='גובה (מ"מ)',
          aspectmode="data",
      ),
      height=550,
      margin=dict(l=10, r=10, b=10, t=40),
  )

  st.plotly_chart(fig, use_container_width=True)

  # ==========================================
  # 8. טבלה מתקפלת לצפייה בכל המק"טים במאגר
  # ==========================================
  with st.expander("📋 לחץ כאן לצפייה וחיפוש בכל רשימת המק\"טים מהמאגר"):
    st.dataframe(
        df_items[["SKU", "Item_Name", "Box_L", "Box_W", "Box_H"]],
        use_container_width=True,
    )
