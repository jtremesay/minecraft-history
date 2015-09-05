<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Minecraft Name History</title>
    </head>
    <body>
        <h1>Minecraft Name History</h1>
        <p>Enter a <em>current</em> or <em>original</em> Minecraft username, or a UUID, and click the button to get the name history.</p>
        <form action="/" method="get">
            <input type="text" name="user" value="{{ user }}" required>
            <input type="submit" value="History Lesson">
        </form>

        % if user_infos is not None:
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Pseudo</th>
                    </tr>
                </thead>

                <tbody>
                    % for user_info in user_infos:
                        <tr>
                            <td>{{ user_info['date'] }}</td>
                            <td>{{ user_info['pseudo'] }}</td>
                        </tr>
                    % end
                </tbody>
            </table>
        % end
        <p>Thank you for not abusing this service.</p>
    </body>
</html>
