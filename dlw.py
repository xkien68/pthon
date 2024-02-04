import requests
import os
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler


async def send_waiting_message(context, chat_id, message="Vui lòng đợi trong giây lát...🕒"):
    # Gọi API để lấy thông tin hình ảnh
    api_url = "https://sumiproject.io.vn/images/anime"
    response = requests.get(api_url)

    if response.status_code == 200:
        image_data = response.json()

        # Lấy URL hình ảnh từ API
        image_url = image_data.get("url", "")

        if image_url:
            # Gửi ảnh cùng với thông báo chờ đợi
            waiting_message = await context.bot.send_photo(chat_id, photo=image_url, caption=message)
            return waiting_message.message_id
        else:
            await context.bot.send_message(chat_id, "Không thể lấy được URL hình ảnh từ API.")
    else:
        await context.bot.send_message(chat_id, "Đã xảy ra lỗi khi gọi API.")

async def start_handler(update: Update, context):
    # Gửi lời chào và hướng dẫn người dùng khi sử dụng bot
    welcome_message = (
    "🌟 Chào mừng bạn đến với Bot của nguyễn văn kiên!\n\n"
    "🚀 Hãy gửi cho tôi một link từ TikTok, CapCut,Facebook hoặc instagram để tải thông tin hoặc video.\n\n"
    "🔍 Để bắt đầu, chỉ cần gửi một đường link từ TikTok, CapCut hoặc Facebook và tôi sẽ giúp bạn tải xuống ảnh vaf video!\n\n"
    "👤 **Giới thiệu về Admin**:\n"
    "Xin chào, tôi là **Nguyễn Văn Kiên**, sinh năm 2006, là người quản trị của Bot này. "
    "Nếu bạn có bất kỳ câu hỏi hoặc gặp vấn đề, hãy thoải mái liên hệ với tôi tại đây(https://t.me/vnkien256). "
    "Chúc bạn có trải nghiệm tuyệt vời!"
    )
    await context.bot.send_message(update.message.chat_id, welcome_message)

async def tiktok_handler(update: Update, context):
    # Gửi thông báo cho người dùng
    waiting_message_id = await send_waiting_message(context, update.message.chat_id)

    tiktok_link = update.message.text

    # Kiểm tra xem đường link có là của www.tiktok.com hoặc vt.tiktok không
    if "www.tiktok.com" in tiktok_link or "vt.tiktok" in tiktok_link:
        api_url_tiktok = f'https://cyq522-8080.csb.app/tiktok/downloadvideo?url={tiktok_link}'

        response = requests.get(api_url_tiktok)

        if response.status_code == 200:
            tiktok_data = response.json()

            # Kiểm tra xem 'data' và 'play' có tồn tại hay không
            if "data" in tiktok_data and "play" in tiktok_data["data"]:
                video_title = tiktok_data['data']['title']
                video_url = tiktok_data['data']['play']
                music_info = tiktok_data['data']['music_info']
                play_count = tiktok_data['data']['play_count']
                digg_count = tiktok_data['data']['digg_count']
                comment_count = tiktok_data['data']['comment_count']
                share_count = tiktok_data['data']['share_count']
                download_count = tiktok_data['data']['download_count']
                collect_count = tiktok_data['data']['collect_count']
                create_time = tiktok_data['data']['create_time']
                unique_id = tiktok_data['data']['author']['unique_id']
                nickname = tiktok_data['data']['author']['nickname']

                # Process each image link
                images = tiktok_data.get('data', {}).get('images', [])
                image_texts = [f"[Link {i + 1}]({image_link})" for i, image_link in enumerate(images)]

                message_text = (
                    f"**Tải video từ TikTok by Nguyen Van Kien**\n"
                    f"title là: {video_title}\n\n"       
                    f"🎵 Âm nhạc: {music_info['title']} bởi {music_info['author']}\n"
                    f"👁‍🗨 Lượt xem: {play_count}\n"
                    f"❤️ Lượt thích: {digg_count}\n"
                    f"💬 Số bình luận: {comment_count}\n"
                    f"🔄 Số chia sẻ: {share_count}\n"
                    f"📥 Số lượt tải về: {download_count}\n"
                    f"🕒 Thời gian tạo: {create_time}\n"
                    f"🆔 ID TikTok: {unique_id}\n"
                    f"👤 Biệt danh: {nickname}\n"
                )

                # Split the message into chunks to avoid caption length issues
                message_chunks = [message_text[i:i+4096] for i in range(0, len(message_text), 4096)]

                # Send images in multiple messages
                for chunk in message_chunks:
                    await update.message.reply_text(chunk)

                # Send video if there are images, else send play
                if images:
                    # Send images
                    for image_link in images:
                        await update.message.reply_photo(photo=image_link)
                        
                else:
                    # Send video
                    await update.message.reply_video(video=video_url)

                # Xóa tin nhắn chờ đợi
                await context.bot.delete_message(update.message.chat_id, waiting_message_id)

                # Xóa video tạm thời sau khi đã gửi
                os.remove("temp_video.mp4")
            else:
                await update.message.reply_text('Dữ liệu không hợp lệ từ API TikTok.')
        else:
            await update.message.reply_text('Đã xảy ra lỗi khi xử lý link TikTok.')
    else:
        await update.message.reply_text('Đường link không hợp lệ.')


async def capcut_handler(update: Update, context):
    # Gửi thông báo cho người dùng
    waiting_message_id = await send_waiting_message(context, update.message.chat_id)

    capcut_link = update.message.text
    api_url_capcut = f'https://sumiproject.io.vn/capcutdowload?url={capcut_link}'

    response = requests.get(api_url_capcut)

    if response.status_code == 200:
        capcut_data = response.json()

        title = capcut_data.get("title", "")
        description = capcut_data.get("description", "")
        usage = capcut_data.get("usage", "")
        video_url = capcut_data.get("video", "")

        # Tải video từ URL
        video_response = requests.get(video_url)
        if video_response.status_code == 200:
            # Lưu video tạm thời
            with open("temp_video.mp4", "wb") as video_file:
                video_file.write(video_response.content)

            # Gửi video tới người dùng
            await context.bot.send_video(chat_id=update.message.chat_id, video=open("temp_video.mp4", "rb"), caption=f"**Thông tin về video từ CapCut**\n📽 Tiêu đề: {title}\n📝 Mô tả: {description}\nLượt Sử dụng: {usage}")

            # Xóa video tạm thời sau khi đã gửi
            await context.bot.delete_message(update.message.chat_id, waiting_message_id)

        else:
            # Xóa tin nhắn chờ đợi nếu có lỗi khi tải video
            await context.bot.delete_message(update.message.chat_id, waiting_message_id)
            await update.message.reply_text('Đã xảy ra lỗi khi tải video từ API.')
    else:
        # Xóa tin nhắn chờ đợi nếu có lỗi khi xử lý link CapCut
        await context.bot.delete_message(update.message.chat_id, waiting_message_id)
        await update.message.reply_text('Đã xảy ra lỗi khi xử lý link CapCut.')


from urllib.parse import urlparse

from urllib.parse import urlparse

async def fb_download_handler(update: Update, context):
    # Gửi thông báo cho người dùng
    waiting_message_id = await send_waiting_message(context, update.message.chat_id)

    fb_link = update.message.text

    # Check if fb_link is a valid URL
    parsed_url = urlparse(fb_link)
    if parsed_url.scheme and parsed_url.netloc:
        api_url_fb = f'https://cyq522-8080.csb.app/fb/download?link={fb_link}'

        response = requests.get(api_url_fb)

        if response.status_code == 200:
            fb_data = response.json()

            # Get the download URL from the API response
            sd_quality_url = fb_data.get("facebookResults", {}).get("result", {}).get("hd_q", "")

            # Check if sd_quality_url is not an empty string
            if sd_quality_url:
                # Download the video
                video_response = requests.get(sd_quality_url)

                # Check if the download was successful
                if video_response.status_code == 200:
                    # Save the video locally (you can customize the file path)
                    with open("downloaded_video.mp4", "wb") as video_file:
                        video_file.write(video_response.content)

                    # Send the video to the user
                    await context.bot.send_video(update.message.chat_id, video=open("downloaded_video.mp4", "rb"))

                    # Optional: Delete the local video file after sending
                    # import os
                    # os.remove("downloaded_video.mp4")

                    # Xóa tin nhắn chờ đợi
                    await context.bot.delete_message(update.message.chat_id, waiting_message_id)

                else:
                    # Xóa tin nhắn chờ đợi nếu có lỗi khi tải video
                    await context.bot.delete_message(update.message.chat_id, waiting_message_id)
                    await update.message.reply_text('Có lỗi xảy ra khi tải video từ link Facebook.')

            else:
                # Xóa tin nhắn chờ đợi nếu không tìm thấy đường link download
                await context.bot.delete_message(update.message.chat_id, waiting_message_id)
                await update.message.reply_text('Không tìm thấy đường link download từ API Facebook.')

        else:
            # Xóa tin nhắn chờ đợi nếu có lỗi khi xử lý link Facebook
            await context.bot.delete_message(update.message.chat_id, waiting_message_id)
            await update.message.reply_text('Có lỗi xảy ra khi xử lý link Facebook.')
    else:
        # Xóa tin nhắn chờ đợi nếu đường link không hợp lệ
        await context.bot.delete_message(update.message.chat_id, waiting_message_id)
        await update.message.reply_text('Đường link không hợp lệ.')




async def download_and_send_thumbnail(context, update, thumbnail_url, instagram_link):
    thumbnail_response = requests.get(thumbnail_url)

    if thumbnail_response.status_code == 200:
        thumbnail_data = thumbnail_response.content
        thumbnail_file = f"{instagram_link.split('/')[-2]}_thumbnail_{thumbnail_url.split('/')[-1]}.jpg"

        await context.bot.send_photo(update.message.chat_id, thumbnail_data, caption=f"ảnh bìa từ Instagram: {instagram_link}", filename=thumbnail_file)
    else:
        await update.message.reply_text(f'Đã xảy ra lỗi khi tải ảnh từ Instagram: {thumbnail_url}')

async def download_and_send_video(context, update, video_url, instagram_link):
    video_response = requests.get(video_url)

    if video_response.status_code == 200:
        video_data = video_response.content
        video_file = f"{instagram_link.split('/')[-2]}.mp4"

        await context.bot.send_video(update.message.chat_id, video_data, caption=f"Video từ Instagram: {instagram_link} ", filename=video_file)
    else:
        await update.message.reply_text('Đã xảy ra lỗi khi tải video từ Instagram.')

async def instagram_handler(update: Update, context):
    # Gửi thông báo cho người dùng
    waiting_message = await send_waiting_message(context, update.message.chat_id)

    try:
        instagram_link = update.message.text
        api_url_instagram = f'https://cyq522-8080.csb.app/instagramdown?link={instagram_link}'

        response = requests.get(api_url_instagram)

        if response.status_code == 200:
            instagram_data = response.json()

            seen_thumbnail_links = set()

            for result in instagram_data["result"]:
                watermark = result.get("wm", "")
                thumbnail_url = result.get("thumbnail", "")
                video_url = result.get("_url", "")

                if thumbnail_url not in seen_thumbnail_links:
                    seen_thumbnail_links.add(thumbnail_url)
                    await download_and_send_thumbnail(context, update, thumbnail_url, instagram_link)
                else:
                    print(f"Ignored duplicate thumbnail link: {thumbnail_url}")

            # Chỉ xử lý video từ kết quả đầu tiên
            video_url = instagram_data["result"][0].get("_url", "")
            await download_and_send_video(context, update, video_url, instagram_link)
        else:
            await update.message.reply_text('Đã xảy ra lỗi khi tải dữ liệu từ Instagram.')

    except telegram.error.BadRequest as e:
        print(f"Lỗi: {e}")
    finally:
        # Xóa tin nhắn chờ đợi nếu là một đối tượng tin nhắn
        if isinstance(waiting_message, telegram.Message):
            await context.bot.delete_message(update.message.chat_id, waiting_message.message_id)

        
        
# Create the application and add the TikTok, CapCut, and Facebook handlers
app = ApplicationBuilder().token("6687957080:AAF4VZ9Wlq7pzcuwb55ynhhlmbFDX2aPIkw").build()
app.add_handler(MessageHandler(filters.Regex(r'https://(www\.tiktok\.com|vt\.tiktok)\S*'), tiktok_handler))
app.add_handler(MessageHandler(filters.Regex(r'https://www\.capcut\.com/\S+'), capcut_handler))
app.add_handler(MessageHandler(filters.Regex(r'https://(www|m)\.facebook\.com\S*'), fb_download_handler))
app.add_handler(MessageHandler(filters.Regex(r'https://www\.instagram\.com/\S+'), instagram_handler))
app.add_handler(CommandHandler("start", start_handler))

# Run the application
app.run_polling()
