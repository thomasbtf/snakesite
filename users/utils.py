import random
import os
import py_avataaars as pa


def create_avatar_image(img_path: str):
    """Creates a random avatar.

    Args:
        img_path (str): Path to the avatar.
    """

    dir = os.path.dirname(img_path)
    if not os.path.exists(dir):
        os.makedirs(dir)

    def r(enum_):
        return random.choice(list(enum_))

    avatar = pa.PyAvataaar(
        style=pa.AvatarStyle.CIRCLE,
        # style=pa.AvatarStyle.TRANSPARENT,
        skin_color=r(pa.SkinColor),
        hair_color=r(pa.HairColor),
        facial_hair_type=r(pa.FacialHairType),
        facial_hair_color=r(pa.HairColor),
        top_type=r(pa.TopType),
        hat_color=r(pa.Color),
        mouth_type=r(pa.MouthType),
        eye_type=r(pa.EyesType),
        eyebrow_type=r(pa.EyebrowType),
        nose_type=r(pa.NoseType),
        accessories_type=r(pa.AccessoriesType),
        clothe_type=r(pa.ClotheType),
        clothe_color=r(pa.Color),
        clothe_graphic_type=r(pa.ClotheGraphicType),
    )
    avatar.render_svg_file(img_path)