import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. הגדרות עמוד ועיצוב CSS מותאם
# ==========================================
st.set_page_config(
    page_title="מערכת אופטימיזציית אריזה 3D - KSP", page_icon="📦", layout="wide"
)

# הרחבת סרגל הכלים הצידי (Sidebar) ועיצוב כרטיסיות
st.markdown(
    """
    <style>
    /* הרחבת סרגל הכלים מצד שמאל */
    [data-testid="stSidebar"] {
        min-width: 420px !important;
        max-width: 420px !important;
    }
    
    /* עיצוב כרטיסיות קרטונים */
    .carton-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px;
        background-color: #f9f9f9;
        text-align: center;
        margin-bottom: 10px;
    }
    .carton-card-active {
        border: 3px solid #2e7d32 !important;
        background-color: #e8f5e9 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .badge-selected {
        background-color: #2e7d32;
        color: white;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.85em;
        font-weight: bold;
    }
    .badge-neutral {
        background-color: #757575;
        color: white;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.85em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📦 מערכת אופטימיזציית אריזה ותצוגת 3D")

# ==========================================
# 2. הגדרת 4 הקרטונים הסופיים במחסן
# ==========================================
CARTONS = {
    "קבוצה 1": {
        "title": "קבוצה 1 (סטנדרטית)",
        "L": 880.0,
        "W": 481.0,
        "H": 295.0,
        "color": "#1f77b4",
    },
    "קבוצה 2": {
        "title": "קבוצה 2 (רחבה/ארוכה)",
        "L": 1910.0,
        "W": 880.0,
        "H": 390.0,
        "color": "#ff7f0e",
    },
    "קבוצה 3": {
        "title": "קבוצה 3 (נפחית/גבוהה)",
        "L": 1020.0,
        "W": 830.0,
        "H": 670.0,
        "color": "#9467bd",
    },
    "קבוצה 4": {
        "title": "קבוצה 4 (ארוכה/צרה)",
        "L": 2030.0,
        "W": 460.0,
        "H": 290.0,
        "color": "#17becf",
    },
}


# ==========================================
# 3. מנגנון טעינת נתונים
# ==========================================
@st.cache_data(ttl=600)
def load_all_products():
  try:
    df = pd.read_csv("products.csv")
    cols = {str(c).strip(): str(c).strip() for c in df.columns}
    df.rename(columns=cols, inplace=True)

    sku_col = next(
        (
            c
            for c in df.columns
            if "sku" in c.lower() or "מק" in c or "id" in c.lower()
        ),
        df.columns[0],
    )
    name_col = next(
        (
            c
            for c in df.columns
            if "name" in c.lower()
            or "item" in c.lower()
            or "שם" in c
            or "desc" in c.lower()
        ),
        df.columns[1],
    )
    l_col = next(
        (
            c
            for c in df.columns
            if "box_l" in c.lower()
            or "length" in c.lower()
            or c.lower() == "l"
            or "אורך" in c
        ),
        None,
    )
    w_col = next(
        (
            c
            for c in df.columns
            if "box_w" in c.lower()
            or "width" in c.lower()
            or c.lower() == "w"
            or "רוחב" in c
        ),
        None,
    )
    h_col = next(
        (
            c
            for c in df.columns
            if "box_h" in c.lower()
            or "height" in c.lower()
            or c.lower() == "h"
            or "גובה" in c
        ),
        None,
    )

    if l_col and w_col and h_col:
      df_clean = df[[sku_col, name_col, l_col, w_col, h_col]].copy()
      df_clean.columns = ["SKU", "Item_Name", "Box_L", "Box_W", "Box_H"]
      df_clean["SKU"] = df_clean["SKU"].astype(str)
      df_clean["Box_L"] = pd.to_numeric(df_clean["Box_L"], errors="coerce")
      df_clean["Box_W"] = pd.to_numeric(df_clean["Box_W"], errors="coerce")
      df_clean["Box_H"] = pd.to_numeric(df_clean["Box_H"], errors="coerce")
      df_clean.dropna(subset=["Box_L", "Box_W", "Box_H"], inplace=True)
      return df_clean, "CSV"
  except Exception:
    pass

  mock_df = pd.DataFrame([
      {
          "SKU": "100019",
          "Item_Name": "Hamilton 20 Inch Standing Fan Heavy Duty",
          "Box_L": 620.0,
          "Box_W": 400.0,
          "Box_H": 180.0,
      },
      {
          "SKU": "200045",
          "Item_Name": "מקלדת מכנית גיימינג אלחוטית",
          "Box_L": 450.0,
          "Box_W": 150.0,
          "Box_H": 40.0,
      },
  ])
  return mock_df, "Mock"


df_items, data_source = load_all_products()

if data_source == "CSV":
  st.sidebar.success(f'🟢 נטענו {len(df_items)} מק"טים מקובץ ה-CSV במאגר!')
else:
  st.sidebar.info(
      '💡 טוען נתוני מדגם. העלה קובץ products.csv למאגר לטעינת כל המק"טים.'
  )

# ==========================================
# 4. סיידבאר: לבחירה מתוך המאגר
# ==========================================
st.sidebar.header("🔎 איתור מוצר מהמלאי")
search_mode = st.sidebar.radio(
    "שיטת בחירה:", ["בחירה מרשימת המק\"טים המלאה", "הזנת מידות ידנית"]
)

item_L, item_W, item_H = 0.0, 0.0, 0.0
item_name_full = ""
sku_val = ""

if search_mode == 'בחירה מרשימת המק"טים המלאה':
  df_items["display_name"] = (
      df_items["SKU"] + " - " + df_items["Item_Name"].fillna("ללא שם")
  )
  selected_display = st.sidebar.selectbox(
      f'חפש או בחר מק"ט ({len(df_items)} זמינים):',
      options=df_items["display_name"].tolist(),
  )

  selected_row = df_items[df_items["display_name"] == selected_display].iloc[0]
  item_L = float(selected_row["Box_L"])
  item_W = float(selected_row["Box_W"])
  item_H = float(selected_row["Box_H"])
  item_name_full = str(selected_row["Item_Name"])
  sku_val = str(selected_row["SKU"])
else:
  st.sidebar.subheader("מידות המוצר (מ\"מ)")
  item_L = st.sidebar.number_input("אורך L", min_value=10.0, value=500.0)
  item_W = st.sidebar.number_input("רוחב W", min_value=10.0, value=300.0)
  item_H = st.sidebar.number_input("גובה H", min_value=10.0, value=150.0)
  item_name_full = "מוצר בהזנה ידנית"
  sku_val = "ידני"

# ==========================================
# 5. לוגיקת התאמת קרטון
# ==========================================
item_volume = item_L * item_W * item_H
valid_options = []

for key, dims in CARTONS.items():
  if item_L <= dims["L"] and item_W <= dims["W"] and item_H <= dims["H"]:
    carton_vol = dims["L"] * dims["W"] * dims["H"]
    utilization = (item_volume / carton_vol) * 100
    waste = carton_vol - item_volume
    valid_options.append({
        "key": key,
        "dims": dims,
        "utilization": utilization,
        "waste": waste,
    })

best_carton_key = (
    min(valid_options, key=lambda x: x["waste"])["key"]
    if valid_options
    else None
)

# ==========================================
# 6. תצוגת פרטי המוצר שנבחר (שם מלא בולט)
# ==========================================
st.markdown(
    f"""
    <div style="background-color: #f0f4f8; padding: 15px; border-radius: 10px; border-right: 6px solid #1f77b4; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #1c3d5a;">🛒 מוצר שנבחר: <b>{item_name_full}</b></h3>
        <p style="margin: 5px 0 0 0; color: #555; font-size: 1.1em;">
            <b>מק"ט:</b> {sku_val} &nbsp;|&nbsp; 
            <b>מידות מוצר:</b> {int(item_L)} x {int(item_W)} x {int(item_H)} מ"מ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 7. תצוגת 4 הקרטונים במחסן והדגשת הנבחר
# ==========================================
st.subheader("📋 מפרט 4 הקרטונים במחסן והתאמה:")
col_c1, col_c2, col_c3, col_c4 = st.columns(4)

cols = [col_c1, col_c2, col_c3, col_c4]

for idx, (key, dims) in enumerate(CARTONS.items()):
  is_selected = key == best_carton_key

  # חישוב אחוז ניצול לכרטיסייה במידה וזה הקרטון הנבחר
  util_text = ""
  if is_selected and valid_options:
    best_opt = next(o for o in valid_options if o["key"] == key)
    util_text = f"<br><b>ניצול נפח:</b> {best_opt['utilization']:.1f}%"

  card_class = "carton-card carton-card-active" if is_selected else "carton-card"
  badge_html = (
      '<span class="badge-selected">🎯 נבחר עבור המוצר</span>'
      if is_selected
      else '<span class="badge-neutral">זמין במחסן</span>'
  )

  with cols[idx]:
    st.markdown(
        f"""
        <div class="{card_class}">
            {badge_html}
            <h4 style="margin: 8px 0 4px 0;">{dims['title']}</h4>
            <p style="margin: 0; color: #444; font-size: 0.95em;">
                <b>{int(dims['L'])} x {int(dims['W'])} x {int(dims['H'])}</b> מ"מ
                {util_text}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ==========================================
# 8. הדמיית תלת-ממד (3D)
# ==========================================
if not valid_options:
  st.error(
      f"🚨 המוצר **{item_name_full}** ({item_L}x{item_W}x{item_H} מ\"מ) חורג"
      " ממידות כל 4 הקרטונים במחסן!"
  )
else:
  best = min(valid_options, key=lambda x: x["waste"])


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

  # קרטון חיצוני נבחר
  fig.add_trace(
      get_box_mesh(
          0,
          0,
          0,
          best["dims"]["L"],
          best["dims"]["W"],
          best["dims"]["H"],
          best["dims"]["title"],
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

  # מוצר פנימי
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
          text=f"<b>הדמיית אריזה בתלת-ממד עבור {best['dims']['title']}</b>",
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
# 9. טבלה מתקפלת לצפייה בכל המאגר
# ==========================================
with st.expander(
    f'📋 לחץ כאן לצפייה וחיפוש בכל רשימת המק"טים ({len(df_items)} פריטים)'
):
  st.dataframe(
      df_items[["SKU", "Item_Name", "Box_L", "Box_W", "Box_H"]],
      use_container_width=True,
  )
