import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. הגדרות עמוד ו-CSS רספונסיבי
# ==========================================
st.set_page_config(
    page_title="מערכת אופטימיזציית אריזה 3D - KSP",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* עיצוב כללי ויישור ימני */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* מרווחי עמוד ראשי - הוספת רווח עליון לקבלת הפריים */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 98% !important;
    }

    /* כותרת ראשית ממורכזת ומשוחררת בחלק העליון */
    .main-header {
        text-align: center !important;
        margin-top: 8px !important;
        margin-bottom: 12px !important;
        color: #0f172a;
        font-size: 1.4rem;
        font-weight: 700;
    }

    /* קופסת פרטי המוצר שנבחר */
    .product-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-right: 5px solid #2563eb;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
    }
    .product-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.25;
    }
    .product-info-line {
        font-size: 0.88rem;
        color: #334155;
        margin-top: 2px;
    }

    /* עיצוב כרטיסיות הקרטונים */
    .carton-card {
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 6px 4px;
        background-color: #ffffff;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 4px;
    }
    .carton-card-selected {
        border: 2px solid #16a34a !important;
        background-color: #f0fdf4 !important;
    }
    .badge-selected {
        background-color: #16a34a;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 1px 5px;
        border-radius: 4px;
        display: inline-block;
    }
    .badge-normal {
        background-color: #64748b;
        color: #ffffff;
        font-size: 0.72rem;
        padding: 1px 5px;
        border-radius: 4px;
        display: inline-block;
    }
    .carton-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2px 0;
    }
    .carton-img-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 36px;
        margin: 2px 0;
    }
    .dims-breakdown {
        font-size: 0.78rem;
        color: #334155;
        background-color: #f8fafc;
        border-radius: 4px;
        padding: 3px;
        margin-top: 3px;
        border: 1px solid #e2e8f0;
        line-height: 1.25;
    }
    .carton-util {
        font-size: 0.82rem;
        font-weight: 700;
        color: #15803d;
        margin-top: 3px;
    }

    /* חוקי CSS מיוחדים למובייל */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1.2rem !important;
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
        }
        .main-header {
            font-size: 1.15rem !important;
            margin-top: 6px !important;
            margin-bottom: 8px !important;
        }
        .product-title {
            font-size: 0.92rem !important;
        }
        .product-info-line {
            font-size: 0.8rem !important;
        }
        .carton-title {
            font-size: 0.8rem !important;
        }
        .dims-breakdown {
            font-size: 0.72rem !important;
            padding: 2px !important;
        }
        .carton-util {
            font-size: 0.78rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# כותרת ראשית ממורכזת ובמיקום מדויק
st.markdown(
    "<div class='main-header'>📦 מערכת אופטימיזציית אריזה 3D</div>",
    unsafe_allow_html=True,
)

# ==========================================
# 2. הגדרת 4 הקרטונים במחסן
# ==========================================
CARTONS = {
    "קבוצה 1": {
        "title": "קבוצה 1 (סטנדרטית)",
        "L": 880.0,
        "W": 481.0,
        "H": 295.0,
        "color": "#1f77b4",
        "svg": """<svg width="50" height="34" viewBox="0 0 70 45"><path d="M35 5 L60 16 L35 27 L10 16 Z" fill="#f59e0b" stroke="#b45309"/><path d="M10 16 L35 27 L35 42 L10 31 Z" fill="#d97706" stroke="#b45309"/><path d="M35 27 L60 16 L60 31 L35 42 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
    "קבוצה 2": {
        "title": "קבוצה 2 (רחבה/ארוכה)",
        "L": 1910.0,
        "W": 880.0,
        "H": 390.0,
        "color": "#ff7f0e",
        "svg": """<svg width="60" height="28" viewBox="0 0 85 40"><path d="M42.5 5 L80 14 L42.5 23 L5 14 Z" fill="#f59e0b" stroke="#b45309"/><path d="M5 14 L42.5 23 L42.5 35 L5 26 Z" fill="#d97706" stroke="#b45309"/><path d="M42.5 23 L80 14 L80 26 L42.5 35 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
    "קבוצה 3": {
        "title": "קבוצה 3 (נפחית/גבוהה)",
        "L": 1020.0,
        "W": 830.0,
        "H": 670.0,
        "color": "#9467bd",
        "svg": """<svg width="40" height="38" viewBox="0 0 60 55"><path d="M30 4 L52 14 L30 24 L8 14 Z" fill="#f59e0b" stroke="#b45309"/><path d="M8 14 L30 24 L30 50 L8 40 Z" fill="#d97706" stroke="#b45309"/><path d="M30 24 L52 14 L52 40 L30 50 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
    "קבוצה 4": {
        "title": "קבוצה 4 (ארוכה/צרה)",
        "L": 2030.0,
        "W": 460.0,
        "H": 290.0,
        "color": "#17becf",
        "svg": """<svg width="65" height="24" viewBox="0 0 90 32"><path d="M45 4 L85 10 L45 16 L5 10 Z" fill="#f59e0b" stroke="#b45309"/><path d="M5 10 L45 16 L45 28 L5 22 Z" fill="#d97706" stroke="#b45309"/><path d="M45 16 L85 10 L85 22 L45 28 Z" fill="#b45309" stroke="#78350f"/></svg>""",
    },
}


def safe_clean_sku(val):
  s = str(val).strip()
  if s.endswith(".0"):
    return s[:-2]
  return s


# ==========================================
# 3. טעינת נתונים
# ==========================================
@st.cache_data(ttl=1)
def load_all_products():
  if os.path.exists("products.csv"):
    try:
      try:
        df = pd.read_csv("products.csv", encoding="utf-8")
      except Exception:
        df = pd.read_csv("products.csv", encoding="utf-8-sig")

      df.columns = [str(c).strip() for c in df.columns]

      sku_c = next((c for c in df.columns if "sku" in c.lower()), None)
      name_c = next((c for c in df.columns if "name" in c.lower()), None)
      length_c = next((c for c in df.columns if "length" in c.lower()), None)
      width_c = next((c for c in df.columns if "width" in c.lower()), None)
      height_c = next((c for c in df.columns if "height" in c.lower()), None)

      if sku_c and name_c and length_c and width_c and height_c:
        df_clean = pd.DataFrame({
            "SKU": df[sku_c].apply(safe_clean_sku),
            "Item_Name": df[name_c].astype(str),
            "Box_L": pd.to_numeric(df[length_c], errors="coerce"),
            "Box_W": pd.to_numeric(df[width_c], errors="coerce"),
            "Box_H": pd.to_numeric(df[height_c], errors="coerce"),
        })

        df_clean.dropna(subset=["Box_L", "Box_W", "Box_H"], inplace=True)
        return df_clean, "CSV"
    except Exception:
      pass

  mock_df = pd.DataFrame([
      {
          "SKU": "100019",
          "Item_Name": "Hemilton 20 Inch Standing Fan 3 Speeds HEM-632",
          "Box_L": 690.0,
          "Box_W": 560.0,
          "Box_H": 140.0,
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

# ==========================================
# 4. תיבת חיפוש
# ==========================================
with st.container():
  search_mode = st.radio(
      "אופן החיפוש:",
      ["מרשימת המאגר", "הזנת מידות ידנית"],
      horizontal=True,
      label_visibility="collapsed",
  )

  item_L, item_W, item_H = 0.0, 0.0, 0.0
  item_name_full = ""
  sku_val = ""

  if search_mode == "מרשימת המאגר":
    df_items["display_name"] = (
        df_items["SKU"] + " - " + df_items["Item_Name"].fillna("ללא שם")
    )
    selected_display = st.selectbox(
        f'חפש מק"ט או שם מוצר ({len(df_items)} זמינים):',
        options=df_items["display_name"].tolist(),
        label_visibility="collapsed",
    )

    selected_row = df_items[
        df_items["display_name"] == selected_display
    ].iloc[0]
    item_L = float(selected_row["Box_L"])
    item_W = float(selected_row["Box_W"])
    item_H = float(selected_row["Box_H"])
    item_name_full = str(selected_row["Item_Name"])
    sku_val = str(selected_row["SKU"])
  else:
    c1, c2, c3 = st.columns(3)
    item_L = c1.number_input("אורך (מ\"מ)", min_value=10.0, value=500.0)
    item_W = c2.number_input("רוחב (מ\"מ)", min_value=10.0, value=300.0)
    item_H = c3.number_input("גובה (מ\"מ)", min_value=10.0, value=150.0)
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
# 6. תצוגת פרטי המוצר
# ==========================================
st.markdown(
    f"""<div class="product-box">
        <div class="product-title">🛒 מוצר שנבחר: {item_name_full}</div>
        <div class="product-info-line"><b>מק"ט:</b> {sku_val}</div>
        <div class="product-info-line"><b>מידות המוצר:</b> אורך <b>{int(item_L)}</b> מ"מ | רוחב <b>{int(item_W)}</b> מ"מ | גובה <b>{int(item_H)}</b> מ"מ</div>
    </div>""",
    unsafe_allow_html=True,
)

# ==========================================
# 7. מפרט 4 הקרטונים במחסן
# ==========================================
st.markdown(
    "<div style='font-weight: 700; font-size: 0.9rem; margin: 2px 0 4px 0;'>📋"
    " מפרט הקרטונים במחסן והתאמה:</div>",
    unsafe_allow_html=True,
)

cols = st.columns(4)

for idx, (key, dims) in enumerate(CARTONS.items()):
  is_selected = key == best_carton_key

  card_class = "carton-card carton-card-selected" if is_selected else "carton-card"
  badge = (
      '<span class="badge-selected">🎯 נבחר</span>'
      if is_selected
      else '<span class="badge-normal">זמין</span>'
  )

  util_html = ""
  if is_selected and valid_options:
    best_opt = next(o for o in valid_options if o["key"] == key)
    util_html = (
        f'<div class="carton-util">ניצול נפח:'
        f' {best_opt["utilization"]:.1f}%</div>'
    )

  card_html = (
      f'<div class="{card_class}">{badge}<div'
      f' class="carton-img-container">{dims["svg"]}</div><div'
      f' class="carton-title">{dims["title"]}</div><div'
      f' class="dims-breakdown"><b>אורך:</b> {int(dims["L"])} מ"מ<br><b>רוחב:</b>'
      f' {int(dims["W"])} מ"מ<br><b>גובה:</b> {int(dims["H"])}'
      f" מ\"מ</div>{util_html}</div>"
  )

  cols[idx].markdown(card_html, unsafe_allow_html=True)

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
          text=f"<b>הדמיית 3D עבור {best['dims']['title']}</b>",
          x=0.5,
          font=dict(size=14),
      ),
      scene=dict(
          xaxis_title='אורך (מ"מ)',
          yaxis_title='רוחב (מ"מ)',
          zaxis_title='גובה (מ"מ)',
          aspectmode="data",
      ),
      height=380,
      margin=dict(l=0, r=0, b=0, t=20),
  )

  st.plotly_chart(
      fig,
      use_container_width=True,
      config={"responsive": True, "displayModeBar": False},
  )

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
