import pandas as pd
import os
import json
from datetime import datetime 
def build_author(post_id, author):
    return {
        'post_id' : post_id,
        'author_id': author['id'],
        'profileUrl': author['profileUrl'],
        'name': author['name'],
        'nickName': author['nickName'],
        'verified': author['verified'],
        'signature': author['signature'],
        'bioLink': author['bioLink'],
        'avatar': author['avatar'],
        'originalAvatarUrl': author['originalAvatarUrl'],
        'privateAccount': author['privateAccount'],
        'following': author['following'],
        'fans': author['fans'],
        'heart': author['heart'],
        'video': author['video'],
        'digg': author['digg'],
        }
def build_post(data_dict):
    return {
        'post_id' : data_dict['id'],
        'text' : data_dict['text'],
        'createTimeISO' : data_dict['createTimeISO'],
        'webVideoUrl' : data_dict['webVideoUrl'],
        'searchQuery' : data_dict['searchQuery'],
        'createTime' : data_dict['createTime'],
        'diggCount' : data_dict['diggCount'],
        'shareCount' : data_dict['shareCount'],
        'playCount' : data_dict['playCount'],
        'collectCount' : data_dict['collectCount'],
        'commentCount' : data_dict['commentCount'],
        'isAd' : data_dict['isAd'],
        'isMuted' : data_dict['isMuted'],
        'isSlideshow' : data_dict['isSlideshow'],
        'isPinned' : data_dict['isPinned']
        }
def build_video_music(post_id, video, music):
    return {
        'post_id': post_id,
        'height': video['height'],
        'width': video['width'],
        'duration': video['duration'],
        'coverUrl': video['coverUrl'],
        'originalCoverUrl': video['originalCoverUrl'],
        'format': video['format'],
        'musicName':music['musicName'],
        'musicAuthor':music['musicAuthor'],
        'musicOriginal':music['musicOriginal'],
        'musicAlbum':music['musicAlbum'],
        'playUrl':music['playUrl'],
        'coverMediumUrl':music['coverMediumUrl'],
        'originalCoverMediumUrl':music['originalCoverMediumUrl'],
        'music_id':music['musicId'],
        }
def cargar_columnas():
    return {
        "post": ['post_id', 'text', 'createTimeISO', 'webVideoUrl', 'searchQuery', 'createTime', 'diggCount', 'shareCount', 'playCount', 'collectCount', 'commentCount', 'isAd', 'isMuted', 'isSlideshow', 'isPinned'],
        "author": ['post_id', 'author_id', 'profileUrl', 'name', 'nickName', 'verified', 'signature', 'bioLink', 'avatar', 'originalAvatarUrl', 'privateAccount', 'following', 'fans', 'heart', 'video', 'digg'],
        "post_video_music": ['post_id', 'height', 'width', 'duration', 'coverUrl', 'originalCoverUrl', 'format', 'musicName', 'musicAuthor', 'musicOriginal', 'musicAlbum', 'playUrl', 'coverMediumUrl', 'originalCoverMediumUrl', 'music_id'],
        "post_author": ['author_id', 'post_id'],
        "post_hastags": ['post_id', 'id', 'name', 'title', 'cover'],
    }

def ParseData_Mejorado(data, dir_data, name_user):
  author_list = []
  post_list = []
  post_video_music_list = []
  post_author_list = []
  post_hashtag_list = []
  for item in data:
    post_id = item['id']
  #------------------- aca se cargan las relaciones -------------------------------#
    post_author_list.append({'post_id': post_id, 'author_id': item['authorMeta']['id']})
    post_hashtag_list = post_hashtag_list + [ {'post_id':post_id} | hastag for hastag in item['hashtags']]
  #------------------- aca se cargan los csv principales --------------------------#
    author_list.append(build_author(post_id=post_id, author=item['authorMeta']))
    post_list.append(build_post(data_dict=item))
    post_video_music_list.append(build_video_music(post_id=post_id, video=item['videoMeta'],music=item['musicMeta']))
  columnas = cargar_columnas()

  #------------------- Se crea el folder local de los nuevos datos  --------------------------#
  curret_date = datetime.now().strftime('%y%m%d%H%M')
  dir_user = name_user + curret_date
  dir_user = os.path.join(dir_data, dir_user)
  os.mkdir(dir_user)

  #------------------- Se crean los path a cada csv --------------------------#
  path_post = os.path.join(dir_user,"post.csv")
  path_author = os.path.join(dir_user,"author.csv")
  path_post_author = os.path.join(dir_user,"post_author.csv")
  path_post_video_music = os.path.join(dir_user,"post_video_music.csv")
  path_post_hashtag = os.path.join(dir_user,"post_hashtag.csv")

  #------------------- Se guardan los CSVSs  --------------------------#
  pd.DataFrame(post_list, columns=columnas['post']).to_csv(path_post, index=False)
  pd.DataFrame(author_list, columns=columnas['author']).to_csv(path_author, index=False)
  pd.DataFrame(post_author_list, columns=columnas['post_author']).to_csv(path_post_author, index=False)
  pd.DataFrame(post_video_music_list, columns=columnas['post_video_music']).to_csv(path_post_video_music, index=False)
  pd.DataFrame(post_hashtag_list, columns=columnas['post_hastags']).to_csv(path_post_hashtag, index=False)
  
  #------------------- Se retorna le path de cada uno --------------------------#
  return { "timestamp" : curret_date, "files": [(path_post, 'post.csv'), (path_author, 'author.csv'), (path_post_author, 'post_author.csv'), (path_post_video_music, 'post_video_music.csv'), (path_post_hashtag, 'post_hashtag.csv')]}
  
